# 터미널이나 publisher의 usb_cam_node_exe가 발행하는 이미지를 구독함.
import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from cv_bridge import CvBridge

import cv2

class ImageSub1(Node):
    def __init__(self):
        super().__init__('img_sub1')

        self.bridge = CvBridge()

        self.subber = self.create_subscription(
            Image,
            '/image_raw',
            self.image_callback,
            10
        )

        self.get_logger().info('img_sub1 노드 시작. /image_raw 토픽 구독')

    def image_callback(self, msg):
        try:
            #ROS2 Image 메시지 -> OpenCV 이미지(Numpy 배열)
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

            # 예제 처리: 흑백 변환
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # 화면 출력
            cv2.imshow("Original", frame)
            cv2.imshow("Gray", gray)

            # waitKey가 있어야 창이 갱신됨
            cv2.waitKey(1)

        except Exception as e:
            self.get_logger().error(f'이미지 변환 에러: {e}')

def main(args=None):
    rclpy.init(args=args)

    node1 = ImageSub1()

    try:
        rclpy.spin(node1)
    except KeyboardInterrupt:
        pass
        
    node1.destroy_node()
    cv2.destroyAllWindows()
    rclpy.shutdown()

if __name__=='__main__':
    main()