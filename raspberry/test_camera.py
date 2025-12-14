#!/usr/bin/env python3
"""
라즈베리파이 카메라 테스트 스크립트
실행: python3 test_camera.py
"""
import sys
import time

def test_picamera2():
    """Picamera2로 카메라 테스트"""
    print("=" * 50)
    print("🎥 Picamera2 카메라 테스트")
    print("=" * 50)
    
    try:
        from picamera2 import Picamera2
        print("✅ Picamera2 임포트 성공")
    except ImportError as e:
        print(f"❌ Picamera2 임포트 실패: {e}")
        print("   설치: sudo apt install python3-picamera2")
        return False
    
    try:
        # 카메라 목록 확인
        print("\n📋 사용 가능한 카메라:")
        picam2 = Picamera2()
        print(f"   카메라 정보: {picam2.camera_properties}")
        
        # 설정
        print("\n⚙️ 카메라 설정 중...")
        config = picam2.create_still_configuration(
            main={"size": (1280, 720)}
        )
        picam2.configure(config)
        
        # 시작
        print("▶️ 카메라 시작...")
        picam2.start()
        time.sleep(2)  # 카메라 안정화 대기
        
        # 캡처
        print("📸 이미지 캡처 중...")
        picam2.capture_file("test_capture.jpg")
        
        # 정지
        picam2.stop()
        picam2.close()
        
        print("\n✅ 카메라 테스트 성공!")
        print("   📁 test_capture.jpg 파일이 생성되었습니다.")
        return True
        
    except Exception as e:
        print(f"\n❌ 카메라 오류: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_opencv():
    """OpenCV로 카메라 테스트"""
    print("\n" + "=" * 50)
    print("🎥 OpenCV 카메라 테스트")
    print("=" * 50)
    
    try:
        import cv2
        print("✅ OpenCV 임포트 성공")
        print(f"   버전: {cv2.__version__}")
    except ImportError as e:
        print(f"❌ OpenCV 임포트 실패: {e}")
        return False
    
    try:
        # /dev/video0 열기
        print("\n📹 /dev/video0 열기 시도...")
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ /dev/video0 열기 실패")
            return False
        
        print("✅ 카메라 열기 성공")
        
        # 프레임 캡처
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            cv2.imwrite("test_opencv.jpg", frame)
            print("✅ OpenCV 테스트 성공!")
            print("   📁 test_opencv.jpg 파일이 생성되었습니다.")
            return True
        else:
            print("❌ 프레임 읽기 실패")
            return False
            
    except Exception as e:
        print(f"❌ OpenCV 오류: {e}")
        return False


def check_video_devices():
    """비디오 장치 확인"""
    print("\n" + "=" * 50)
    print("📹 비디오 장치 확인")
    print("=" * 50)
    
    import os
    import glob
    
    devices = glob.glob("/dev/video*")
    if devices:
        print("✅ 비디오 장치 발견:")
        for dev in sorted(devices):
            print(f"   {dev}")
    else:
        print("❌ /dev/video* 장치가 없습니다.")
        print("   카메라 연결 및 활성화를 확인하세요.")
    
    # media 장치 확인
    media_devices = glob.glob("/dev/media*")
    if media_devices:
        print("\n📹 미디어 장치:")
        for dev in sorted(media_devices):
            print(f"   {dev}")


def check_camera_module():
    """카메라 모듈 상태 확인"""
    print("\n" + "=" * 50)
    print("🔍 카메라 모듈 상태")
    print("=" * 50)
    
    import subprocess
    
    # vcgencmd
    try:
        result = subprocess.run(
            ["vcgencmd", "get_camera"],
            capture_output=True,
            text=True
        )
        print(f"vcgencmd get_camera: {result.stdout.strip()}")
    except Exception as e:
        print(f"vcgencmd 실행 실패: {e}")
    
    # dmesg 카메라 관련
    try:
        result = subprocess.run(
            ["dmesg"],
            capture_output=True,
            text=True
        )
        lines = [l for l in result.stdout.split('\n') 
                 if 'camera' in l.lower() or 'imx' in l.lower() or 'ov5647' in l.lower()]
        if lines:
            print("\ndmesg 카메라 관련:")
            for line in lines[-5:]:  # 마지막 5줄만
                print(f"   {line}")
    except Exception:
        pass


def test_all_camera_ports():
    """모든 카메라 포트 테스트 (Pi 5용)"""
    print("\n" + "=" * 50)
    print("🔌 Pi 5 카메라 포트 전체 테스트")
    print("=" * 50)
    
    try:
        from picamera2 import Picamera2
    except ImportError:
        print("❌ Picamera2가 설치되지 않았습니다.")
        return
    
    # 전체 카메라 목록 확인
    print("\n📋 감지된 카메라 목록:")
    try:
        cameras = Picamera2.global_camera_info()
        if cameras:
            for i, cam in enumerate(cameras):
                print(f"   [{i}] {cam}")
        else:
            print("   ❌ 감지된 카메라가 없습니다.")
    except Exception as e:
        print(f"   ❌ 카메라 목록 조회 실패: {e}")
    
    # 각 카메라 번호로 시도
    print("\n🔍 카메라 인덱스별 테스트:")
    for cam_num in range(2):  # CAM0, CAM1
        print(f"\n   --- 카메라 {cam_num} (CAM{cam_num}) ---")
        try:
            picam2 = Picamera2(camera_num=cam_num)
            config = picam2.create_still_configuration(main={"size": (640, 480)})
            picam2.configure(config)
            picam2.start()
            import time
            time.sleep(1)
            filename = f"test_cam{cam_num}.jpg"
            picam2.capture_file(filename)
            picam2.stop()
            picam2.close()
            print(f"   ✅ CAM{cam_num} 성공! {filename} 생성됨")
        except IndexError:
            print(f"   ⚠️ CAM{cam_num}: 카메라가 연결되지 않음")
        except Exception as e:
            print(f"   ❌ CAM{cam_num} 오류: {e}")


def test_rpicam_command():
    """rpicam 명령어로 테스트"""
    print("\n" + "=" * 50)
    print("🎬 rpicam 명령어 테스트")
    print("=" * 50)
    
    import subprocess
    
    # rpicam-hello --list-cameras
    print("\n실행: rpicam-hello --list-cameras")
    try:
        result = subprocess.run(
            ["rpicam-hello", "--list-cameras"],
            capture_output=True,
            text=True,
            timeout=10
        )
        print(result.stdout)
        if result.stderr:
            print(f"stderr: {result.stderr}")
    except FileNotFoundError:
        print("❌ rpicam-hello 명령어가 없습니다.")
        print("   libcamera-hello 시도 중...")
        try:
            result = subprocess.run(
                ["libcamera-hello", "--list-cameras"],
                capture_output=True,
                text=True,
                timeout=10
            )
            print(result.stdout)
            if result.stderr:
                print(f"stderr: {result.stderr}")
        except FileNotFoundError:
            print("❌ libcamera-hello도 없습니다.")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    # 각 카메라로 사진 촬영 시도
    for cam_num in range(2):
        print(f"\n실행: rpicam-still --camera {cam_num}")
        try:
            result = subprocess.run(
                ["rpicam-still", "--camera", str(cam_num), 
                 "-o", f"rpicam_test_{cam_num}.jpg", 
                 "-t", "1000", "--nopreview"],
                capture_output=True,
                text=True,
                timeout=15
            )
            if result.returncode == 0:
                print(f"   ✅ CAM{cam_num} 성공! rpicam_test_{cam_num}.jpg")
            else:
                print(f"   ❌ CAM{cam_num} 실패: {result.stderr}")
        except FileNotFoundError:
            print("   rpicam-still 명령어가 없습니다.")
            break
        except subprocess.TimeoutExpired:
            print(f"   ⏱️ CAM{cam_num} 타임아웃")
        except Exception as e:
            print(f"   ❌ 오류: {e}")


if __name__ == "__main__":
    print("🍓 라즈베리파이 카메라 테스트")
    print("=" * 50)
    
    # 비디오 장치 확인
    check_video_devices()
    
    # 카메라 모듈 상태
    check_camera_module()
    
    # rpicam 명령어 테스트
    test_rpicam_command()
    
    # 전체 카메라 포트 테스트
    test_all_camera_ports()
    
    # Picamera2 테스트
    picam_ok = test_picamera2()
    
    # OpenCV 테스트 (Picamera2 실패 시)
    if not picam_ok:
        test_opencv()
    
    print("\n" + "=" * 50)
    print("테스트 완료!")
    print("=" * 50)

