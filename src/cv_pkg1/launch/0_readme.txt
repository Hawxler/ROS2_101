1. cv1.launch.xml
* 터미널에 입력해서 실행하는 론치 파일
* 실행 예
$ ros2 launch cv_pkg1 cv1.launch.xml

2. cv2.launch.xml
* 파라미터(size1.yaml)를 불러와서 적용하는 론치 파일
* img_pub2.py
* 실행 예
$ ros2 launch cv_pkg1 cv2.launch.py

3. cv3.launch.xml
* 파라미터를 추가한 size2.yaml을 불러와서 적용하고 화면에 적용하는 파일
* img_pub3.py

4. cv4.launch.xml
* HSV 색변환
* img_pub3.py가 /image_raw 발행 > img_pub4.py가 cv_bridge로 OpenCV -> HSV 변환 > (H,) S, V 값 변환 > HSV -> OpenCV 변환 > /image_hsv 발행
* 화면 설정, S, V는 size2.yaml을 불러와서 적용함.
* img_pub3.py, img_pub4.py

5. cv5.launch.xml
* Canny Edge Detection
