# Canny Edge detection
# 선 감지 순서: Grey Scale > Blur(점점이 끊어진 선 뭉개서 연결) > Canny edge 적용(low/high threshold 2개 적용)
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np
from rcl_interfaces.msg import ParameterDescriptor, IntegerRange
from rcl_interfaces.msg import SetParametersResult

class CannyEdgeDetector(Node):
    def __init__(self):
        super().__init__('canny_edge_node5')
        self.get_logger().info("캐니 엣지 디텍터 시작")

        #1. 구독자 생성
        self.subber = self.create_subscription(
            Image,
            '/image_raw',
            self.img_callback,
            10
        )

        #2. 발행자 생성
        self.pubber = self.create_publisher(
            Image,
            '/image_edge',
            10
        )

        #3. Trackbar로 조절할 파라미터 설정(threshold 1, 2)
        # IntegerRange(최솟값, 최댓값, 조정 단위)
        param_desc_threshold1 = ParameterDescriptor(
            description='Canny low threshold',
            integer_range=[IntegerRange(from_value=0, to_value=255, step=1)],
        )
        param_desc_threshold2 = ParameterDescriptor(
            description='Canny high threshold',
            integer_range=[IntegerRange(from_value=0, to_value=255, step=1)],
        )

        # min/max threshold 설정(초기값 100, 200)
        self.declare_parameter('low_threshold', 100, param_desc_threshold1)
        self.declare_parameter('high_threshold', 200, param_desc_threshold2)

        low_threshold = self.get_parameter('low_threshold').value
        high_threshold = self.get_parameter('high_threshold').value

        self.get_logger().info(f'low_threshold 초기값: {low_threshold}')
        self.get_logger().info(f'high_threshold 초기값: {high_threshold}')

        # 파라미터 변경되면 callback 실행
        self.add_on_set_parameters_callback(self.para_callback)

        # cv_bridge 생성
        self.bridge1 = CvBridge()

    # 파라미터 변경 시 실행할 콜백: 변경 내용 출력
    def para_callback(self, params):
        for param in params:
            msg = f"{param.name}의 변경된 값: {param.value}"
            self.get_logger().info(msg)

        return SetParametersResult(successful=True)
    
    # 구독자 실행부
    def img_callback(self, msg):
        # 파라미터 값 받아오기
        low_threshold = self.get_parameter('low_threshold').value
        high_threshold = self.get_parameter('high_threshold').value

        # ROS img -> OpenCV img (BGR)
        cv_img = self.bridge1.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # cv img -> grayscale
        gray_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

        # grayscale -> canny edge img
        edges = cv2.Canny(gray_img, low_threshold, high_threshold)

        # canny edge img -> ROS img
        edge_msg = self.bridge1.cv2_to_imgmsg(edges, encoding='mono8')

        # ROS img 발행
        self.pubber.publish(edge_msg)

def main(args=None):
    rclpy.init(args=args)

    node1 = CannyEdgeDetector()
    rclpy.spin(node1)

    node1.destroy_node()
    rclpy.shutdown()

if __name__=='__main__':
    main()