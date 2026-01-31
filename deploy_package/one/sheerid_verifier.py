"""SheerID 学生验证主程序"""
import re
import random
import logging
import httpx
import time
from datetime import datetime
from typing import Dict, Optional, Tuple

from . import config
from .name_generator import NameGenerator, generate_birth_date
from .img_generator import generate_image, generate_edu_email

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class SheerIDVerifier:
    """SheerID 学生身份验证器"""

    def __init__(self, verification_id: str):
        self.verification_id = verification_id
        self.device_fingerprint = self._generate_device_fingerprint()
        
        # Load proxies
        self.proxies_list = []
        try:
            with open("proxies.txt", "r") as f:
                self.proxies_list = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            pass
            
        self._init_http_client()

    def _init_http_client(self):
        """Initializes or re-initializes the HTTP client with a random proxy"""
        proxy = None
        if self.proxies_list:
            # Pick a proxy
            proxy_str = random.choice(self.proxies_list)
            
            # Store current proxy to remove it later if it fails
            self.current_proxy = proxy_str
            
            # Format proxy for httpx if needed
            if not proxy_str.startswith("http"):
                proxy_str = f"http://{proxy_str}"
            proxy = proxy_str
            # Log only the IP part to avoid leaking creds in logs
            safe_proxy = proxy_str.split('@')[-1] if '@' in proxy_str else proxy_str
            logger.info(f"🔄 Switched Proxy: {safe_proxy} (Remaining: {len(self.proxies_list)})")

        # Close existing if any
        if hasattr(self, "http_client"):
            try:
                self.http_client.close()
            except:
                pass
                
        self.http_client = httpx.Client(timeout=30.0, proxies=proxy, verify=False)
        
        # Verify Actual Exit IP (Debug)
        try:
            ip_check = self.http_client.get("https://api64.ipify.org?format=json", timeout=5).json()
            actual_ip = ip_check.get("ip", "Unknown")
            logger.info(f"🌍 Current Exit IP: {actual_ip}")
        except Exception:
            logger.warning("⚠️ Could not verify external IP (Check internet/proxy)")

    def __del__(self):
        if hasattr(self, "http_client"):
            self.http_client.close()

    @staticmethod
    def _generate_device_fingerprint() -> str:
        chars = '0123456789abcdef'
        return ''.join(random.choice(chars) for _ in range(32))

    @staticmethod
    def normalize_url(url: str) -> str:
        """规范化 URL（保留原样）"""
        return url

    @staticmethod
    def parse_verification_id(url: str) -> Optional[str]:
        match = re.search(r"verificationId=([a-f0-9]+)", url, re.IGNORECASE)
        if match:
            return match.group(1)
        return None

    def _init_consistent_headers(self):
        """Generate consistent headers for the entire session"""
        # Randomize Version (124-126) - Newer versions
        version = random.choice(["124", "125", "126"])
        
        # Consistent UA-Platform pair
        self.user_agent = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36"
        
        self.session_headers = {
            "Content-Type": "application/json",
            "User-Agent": self.user_agent,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": "https://services.sheerid.com",
            "Referer": "https://services.sheerid.com/verify/Example_Program/", 
            "Sec-Ch-Ua": f'"Not A(Brand";v="99", "Google Chrome";v="{version}", "Chromium";v="{version}"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }

    def _rotate_proxy(self):
        """Pick a new proxy (without removing the old one)"""
        # Just re-init to pick a random new one
        logger.info("🔄 Rotating Proxy (Random Selection)...")
        self._init_http_client()

    def _sheerid_request(
        self, method: str, url: str, body: Optional[Dict] = None
    ) -> Tuple[Dict, int]:
        """发送 SheerID API 请求 (With Retry & Proxy Rotation)"""
        if not hasattr(self, "session_headers"):
             self._init_consistent_headers()
        
        headers = self.session_headers.copy()

        max_retries = 10 
        for attempt in range(max_retries):
            try:
                response = self.http_client.request(
                    method=method, url=url, json=body, headers=headers
                )
                try:
                    data = response.json()
                except Exception:
                    data = response.text
                
                # Handling 5xx (Server/Proxy Errors) - 429 REMOVED (Treat as Fatal Link Limit)
                if response.status_code in [502, 503, 504]:
                    # Capped Exponential Backoff (Max 60s)
                    wait_time = min((2 ** attempt) + random.randint(1, 3), 60)
                    logger.warning(f"⚠️ Proxy Failed ({response.status_code}). Rotating & Waiting {wait_time}s...")
                    self._rotate_proxy() 
                    time.sleep(wait_time)
                    continue
                    
                return data, response.status_code
                
            except Exception as e:
                logger.error(f"Request Error (Attempt {attempt+1}): {e}")
                if attempt < max_retries - 1:
                    wait_time = 3
                    logger.info(f"Rotating Proxy and Retrying in {wait_time}s...")
                    self._rotate_proxy()
                    time.sleep(wait_time)
                else:
                    raise e
        
        # If loop finishes without return (exhausted retries), raise error
        raise Exception(f"Max retries ({max_retries}) exceeded for {url}")

    def _upload_to_s3(self, upload_url: str, img_data: bytes) -> bool:
        """上传 JPEG 到 S3"""
        try:
            headers = {"Content-Type": "image/jpeg"}
            response = self.http_client.put(
                upload_url, content=img_data, headers=headers, timeout=60.0
            )
            return 200 <= response.status_code < 300
        except Exception as e:
            logger.error(f"S3 上传失败: {e}")
            return False

    def verify(
        self,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        birth_date: str = None,
        school_id: str = None,
    ) -> Dict:
        """执行验证流程"""
        try:
            current_step = "initial"

            if not first_name or not last_name:
                name = NameGenerator.generate()
                first_name = name["first_name"]
                last_name = name["last_name"]

            if not school_id:
                # Optimized: Multi-School Mode (Valid Logos Only)
                # Expanded Pool: 7 Universities (Logos or Text-Fallback)
                # UF(334), OSU(339), ASU(75), NYU(2285), USC(3679), UCLA(3499), Michigan(3589)
                available_schools = ['334', '339', '75', '2285', '3679', '3499', '3589']
                school_id = random.choice(available_schools)
                
            # Fallback if config is missing (safety)
            if school_id not in config.SCHOOLS:
                 school_id = '334' # Default to UF
                 
            school = config.SCHOOLS[school_id]

            if not email:
                email = generate_edu_email(first_name, last_name, school['domain'])
            if not birth_date:
                birth_date = generate_birth_date()

            logger.info(f"Using School: {school['name']} (ID: {school_id})")
            logger.info(f"Student: {first_name} {last_name} | {email}")
            logger.info(f"Verification ID: {self.verification_id}")

            # Define Document Types - STRICT CYCLING (Mobile -> Schedule -> Tuition)
            # As per "Final Update" screenshot strategy
            DOC_TYPES = ['mobile', 'schedule', 'tuition']
            
            # Start with a random one (or prioritize Mobile as per screenshot hint "Pertama coba Mobile ID")
            # Let's keep it random to avoid sticky bans, but the cycle will ensure rotation.
            current_doc_type = random.choice(DOC_TYPES)
            
            logger.info(f"Langkah 1/4: Membuat Dokumen (Tipe: {current_doc_type.upper()})...")
            
            # Generate Initial Image
            img_data = generate_image(first_name, last_name, school_id, doc_type=current_doc_type)
            file_size = len(img_data)
            logger.info(f"✅ Generated {current_doc_type.upper()}: {file_size/1024:.1f}KB")



            # Kirim Data Siswa
            logger.info("Langkah 2/4: Mengirim Data Siswa...")
            step2_body = {
                "firstName": first_name,
                "lastName": last_name,
                "birthDate": birth_date,
                "email": email,
                "phoneNumber": "",
                "organization": {
                    "id": int(school_id),
                    "idExtended": school["idExtended"],
                    "name": school["name"],
                },
                "deviceFingerprintHash": self.device_fingerprint,
                "locale": "en-US",
                "metadata": {
                    "marketConsentValue": False,
                    "refererUrl": f"{config.SHEERID_BASE_URL}/verify/{config.PROGRAM_ID}/?verificationId={self.verification_id}",
                    "verificationId": self.verification_id,
                    "flags": '{"collect-info-step-email-first":"default","doc-upload-considerations":"default","doc-upload-may24":"default","doc-upload-redesign-use-legacy-message-keys":false,"docUpload-assertion-checklist":"default","font-size":"default","include-cvec-field-france-student":"not-labeled-optional"}',
                    "submissionOptIn": "By submitting the personal information above, I acknowledge that my personal information is being collected under the privacy policy of the business from which I am seeking a discount",
                },
            }

            step2_data, step2_status = self._sheerid_request(
                "POST",
                f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/collectStudentPersonalInfo",
                step2_body,
            )

            if step2_status != 200:
                raise Exception(f"Langkah 2 Gagal (Status {step2_status}): {step2_data}")
            if step2_data.get("currentStep") == "error":
                error_msg = ", ".join(step2_data.get("errorIds", ["Unknown error"]))
                raise Exception(f"Langkah 2 Error: {error_msg}")

            logger.info(f"✅ Langkah 2 Selesai: {step2_data.get('currentStep')}")
            current_step = step2_data.get("currentStep", current_step)

            # Lewati SSO (jika perlu)
            if current_step in ["sso", "collectStudentPersonalInfo"]:
                logger.info("Langkah 3/4: Melewati Verifikasi SSO...")
                step3_data, _ = self._sheerid_request(
                    "DELETE",
                    f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/sso",
                )
                logger.info(f"✅ Langkah 3 Selesai: {step3_data.get('currentStep')}")
                current_step = step3_data.get("currentStep", current_step)

            # Unggah dokumen dan selesaikan
            logger.info("Langkah 4/4: Mengunggah Dokumen (Single File)...")
            
            # HUMAN DELAY: Simulate time taken to "take photo" or "find file"
            delay = 10 
            logger.info(f"🧠 Acting Human: Pausing {delay}s before upload...")
            time.sleep(delay)
            # Upload Single File
            # Randomize filename to look like camera upload
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            random_suffix = random.randint(100, 999)
            filename = f"IMG_{timestamp}_{random_suffix}.jpg"
            
            step4_body = {
                "files": [
                    {"fileName": filename, "mimeType": "image/jpeg", "fileSize": file_size}
                ]
            }
            step4_data, step4_status = self._sheerid_request(
                "POST",
                f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/docUpload",
                step4_body,
            )
            
            if not step4_data.get("documents"):
                raise Exception("Gagal mendapatkan URL unggahan")

            # Upload Single File
            upload_url = step4_data["documents"][0]["uploadUrl"]
            logger.info(f"📤 Uploading {current_doc_type.upper()}...")
            
            if not self._upload_to_s3(upload_url, img_data):
                 raise Exception("S3 Upload Failed")
            
            logger.info(f"✅ {current_doc_type.upper()} Uploaded.")
            logger.info("✅ Semua dokumen berhasil diunggah")

            step6_data, _ = self._sheerid_request(
                "POST",
                f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/completeDocUpload",
            )
            logger.info(f"✅ Dokumen Selesai Dikirim: {step6_data.get('currentStep')}")
            final_status = step6_data

            # Polling & Retry Loop (Infinite as requested)
            retry_count = 0
            
            while True:
                retry_count += 1
                logger.info(f"⏳ Status Check ({retry_count})...")
                
                # Check status
                status_data, status_code = self._sheerid_request(
                    "GET", 
                    f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}"
                )
                
                # Check for 429 explicitly here
                if status_code == 429:
                    logger.error("❌ Link Hangus / Limit Exceeded (429).")
                    return {
                        "success": False, 
                        "pending": False, 
                        "message": "Link Hangus / Reset. Get NEW LINK.", 
                        "verification_id": self.verification_id
                    }
                
                current_step_status = status_data.get("currentStep")
                logger.info(f"Current Step: {current_step_status}")
                
                if current_step_status == "success":
                    logger.info("🎉 Verification SUCCESS!")
                    return {
                        "success": True,
                        "pending": False,
                        "message": "Verification Successful!",
                        "verification_id": self.verification_id,
                        "redirect_url": status_data.get("redirectUrl"),
                        "status": status_data
                    }
                
                elif current_step_status in ["error", "limitExceeded"]:
                    logger.error(f"❌ Verification Failed: {current_step_status}")
                    return {
                        "success": False, 
                        "pending": False, 
                        "message": "Verification limit exceeded or error.", 
                        "verification_id": self.verification_id
                    }
                    # Fatal error logic removed as we return immediately above
                    # error_ids = status_data.get("errorIds", [])
                    # ...
                     
                elif current_step_status == "collectStudentPersonalInfo":
                    logger.error("❌ Verification Reset to Initial Step.")
                    return {
                        "success": False, 
                        "pending": False, 
                        "message": "Link Hangus / Reset. Get NEW LINK.", 
                        "verification_id": self.verification_id
                    }

                elif current_step_status in ["docUpload", "uploadDocuments"]:
                    # Soft Rejection -> Retry with NEW Image AND Different Type
                    
                    # Cycle to next doc type
                    current_index = DOC_TYPES.index(current_doc_type)
                    current_doc_type = DOC_TYPES[(current_index + 1) % len(DOC_TYPES)]
                    
                    logger.info(f"♻️ Soft Rejection. Retrying with NEW {current_doc_type.upper()}...")
                    
                    # Regenerate Image (Randomized)
                    img_data = generate_image(first_name, last_name, school_id, doc_type=current_doc_type)
                    file_size = len(img_data)
                    
                    # Randomize filename for retry too
                    retry_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    retry_suffix = random.randint(1000, 9999)
                    retry_filename = f"IMG_{retry_timestamp}_{retry_suffix}.jpg"

                    # Get Upload URL (Step 4 again)
                    step4_body = {
                        "files": [
                            {"fileName": retry_filename, "mimeType": "image/jpeg", "fileSize": file_size}
                        ]
                    }
                    step4_data, _ = self._sheerid_request(
                        "POST",
                        f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/docUpload",
                        step4_body,
                    )
                    
                    if step4_data.get("documents"):
                        upload_url = step4_data["documents"][0]["uploadUrl"]
                        if self._upload_to_s3(upload_url, img_data):
                             logger.info("✅ Re-upload successful. Submitting...")
                             self._sheerid_request(
                                "POST",
                                f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/completeDocUpload",
                            )
                    else:
                        logger.warning("Failed to get new upload URL.")
                        
                elif current_step_status == "pending":
                    # === FORCE RE-UPLOAD ENABLED (BALANCED MODE) ===
                    # Stuck in pending for too long? Force re-upload to nudge the system.
                    # Interval: Every 6 checks (~60 seconds)
                    if retry_count % 6 == 0:
                        # Cycle type (Mobile -> Schedule -> Tuition -> Mobile ...)
                        current_index = DOC_TYPES.index(current_doc_type)
                        current_doc_type = DOC_TYPES[(current_index + 1) % len(DOC_TYPES)]
                        
                        logger.warning(f"⚠️ Terlalu Lama Pending ({retry_count}). Mencoba Upload Ulang {current_doc_type.upper()}...")
                        
                        # === FORCE RE-UPLOAD LOGIC ===
                        img_data = generate_image(first_name, last_name, school_id, doc_type=current_doc_type)
                        file_size = len(img_data)
                        
                        retry_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        retry_suffix = random.randint(1000, 9999)
                        retry_filename = f"IMG_{retry_timestamp}_{retry_suffix}.jpg"
    
                        step4_body = {
                            "files": [
                                {"fileName": retry_filename, "mimeType": "image/jpeg", "fileSize": file_size}
                            ]
                        }
                        
                        try:
                            step4_data, _ = self._sheerid_request(
                                "POST",
                                f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/docUpload",
                                step4_body,
                            )
                            
                            if step4_data.get("documents"):
                                upload_url = step4_data["documents"][0]["uploadUrl"]
                                if self._upload_to_s3(upload_url, img_data):
                                     logger.info("✅ Re-upload Sukses. Mengirim ulang...")
                                     self._sheerid_request(
                                        "POST",
                                        f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/completeDocUpload",
                                    )
                        except Exception as e:
                            logger.warning(f"Gagal Re-upload (mungkin dikunci): {e}")

                    # Still reviewing
                    logger.info("Masih pending... menunggu 10 detik...")
                    time.sleep(10)
                    
                # Unknown state
                    time.sleep(3)
                
                # Timeout Check REMOVED per user request (Processing can take longer)
                
                # retry_count increment is already done at start of loop
            
            # If loop finishes without success (Unreachable in infinite loop but kept for safety structure)
            return {
                "success": True, 
                "pending": True, 
                "message": "Still reviewing after retries.", 
                "verification_id": self.verification_id,
                "status": status_data
            }

        except Exception as e:
            logger.error(f"❌ Verifikasi Gagal: {e}")
            return {"success": False, "message": str(e), "verification_id": self.verification_id}


def main():
    """主函数 - 命令行界面"""
    import sys

    print("=" * 60)
    print("SheerID Verification Tool (Python Version)")
    print("=" * 60)
    print()

    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Masukkan URL Verifikasi SheerID: ").strip()

    if not url:
        print("❌ Error: URL tidak diberikan")
        sys.exit(1)

    verification_id = SheerIDVerifier.parse_verification_id(url)
    if not verification_id:
        print("❌ Error: Format ID Verifikasi tidak valid")
        sys.exit(1)

    print(f"✅ ID Verifikasi ditemukan: {verification_id}")
    print()

    verifier = SheerIDVerifier(verification_id)
    result = verifier.verify()

    print()
    print("=" * 60)
    print("Hasil Verifikasi:")
    print("=" * 60)
    print(f"Status: {'✅ BERHASIL' if result['success'] else '❌ GAGAL'}")
    print(f"Pesan: {result['message']}")
    if result.get("redirect_url"):
        print(f"URL Pengalihan: {result['redirect_url']}")
    print("=" * 60)

    return 0 if result["success"] else 1


if __name__ == "__main__":
    exit(main())
