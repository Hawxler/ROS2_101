import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from cv_bridge import CvBridge

import cv2

class GazeboCvSub(Node):
    def __init__(self):
        super().__init__('r1_cv_sub_node1')

        # 이미지 변환 도구: ROS Image <-> OpenCV image
        self.bridge = CvBridge()

        # /image_raw 구독
        self.subber = self.create_subscription(
            Image,
            '/image_raw',
            self.image_callback,
            10
        )

        self.get_logger().info("Gazebo / image_raw 구독 시작")

    def image_callback(self, msg):
        try:
            # ROS2 이미지 -> OpenCV 이미지로 변환
            frame = self.bridge.imgmsg_to_cv2(
                msg,
                desired_encoding='bgr8'
            )

            # 화면에 표시
            cv2.imshow("Gazebo Cam", frame)

            # imshow 창 갱신
            cv2.waitKey(1)
        
        except Exception as e:
            self.get_logger().error(f'이미지 변환 오류: {e}')

def main(args=None):
    rclpy.init(args=args)

    node1 = GazeboCvSub()

    try:
        rclpy.spin(node1)
    except KeyboardInterrupt:
        node1.get_logger().info("Ctrl+C 입력됨")
    finally:
        cv2.destroyAllWindows()
        node1.destroy_node1()
        rclpy.shutdown()

if __name__ == '__main__':
    main()