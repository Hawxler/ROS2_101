# 1. Gazebo camera /image_raw를 구독해서 
# 2. grayscale + edge 처리 후 
# 3. /image_edge로 발행
import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from cv_bridge import CvBridge

import cv2

class GazeboCvEdge(Node):
    def __init__(self):
        super().__init__('r1_edge_node1')

        # ROS 이미지 <-> OpenCV 이미지 변환 도구
        self.bridge = CvBridge()

        # /image_raw 구독
        self.subber = self.create_subscription(
            Image,
            '/image_raw',
            self.image_callback,
            10
        )

        # 처리된 edge 이미지 발행
        self.pubber = self.create_publisher(
            Image,
            '/image_edge',
            10
        )

        self.get_logger().info('r1_cv_edge1 시작: /image_raw 구독, /image_edge 발행')
    
    def image_callback(self, msg):
        try:
            # 1. ROS2 이미지 -> OpenCV BGR 이미지
            frame = self.bridge.imgmsg_to_cv2(
                msg,
                desired_encoding='bgr8'
            )

            # 2. grayscale 변환
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # 3. Canny edge 검출
            edge = cv2.Canny(gray, 100, 200)

            # 4. OpenCV 창으로 확인
            cv2.imshow("Origial Img", frame)
            cv2.imshow("Gray Img", gray)
            cv2.imshow("Edge Img", edge)
            cv2.waitKey(1)

            # 5. OpenCV edge 이미지 -> ROS2 이미지
            edge_msg = self.bridge.cv2_to_imgmsg(
                edge,
                encoding='mono8'
            )

            # 6. 원본 이미지의 시간 정보와 frame_id를 그대로 복사
            edge_msg.header = msg.header

            # 7. /image_edge 발행
            self.pubber.publish(edge_msg)
        
        except Exception as e:
            self.get_logger().error(f'이미지 처리 오류: {e}')

def main(args=None):
    rclpy.init(args=args)

    node1 = GazeboCvEdge()

    try:
        rclpy.spin(node1)
    except KeyboardInterrupt:
        node1.get_logger().info('Ctrl+C 입력됨')
    finally:
        cv2.destroyAllWindows()
        node1.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()