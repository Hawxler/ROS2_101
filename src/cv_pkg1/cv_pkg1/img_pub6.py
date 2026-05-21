#img_pub3.py에서 이미지 발행 + img_pub6.py에서 카툰 스타일로 변환해서 발행하기
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
# import numpy as np
from rcl_interfaces.msg import ParameterDescriptor # 파라미터 설명 추가
from rcl_interfaces.msg import IntegerRange # 정수형 파라미터 범위 설정
from rcl_interfaces.msg import SetParametersResult # 파라미터 변경 허용 여부 반환

class CartoonPub1(Node):
    def __init__(self):
        super().__init__('cartoon_pub_node6')
        self.get_logger().info("카툰 스타일 변환 노드 시작")

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
            '/image_cartoon',
            10
        )

        #3. 카툰 변환용 파라미터 설정 (sigma_color, sigma_space)
        # sigma_color: 색상 공간에서 얼만큼 떨어진 색을 같은 색으로 인식할지 (값이 클수록 더 많은 색이 같은 색으로 인식됨)
        # sigma_space: 좌표 공간에서 얼만큼 떨어진 픽셀을 같은 픽셀로 인식할지 (값이 클수록 더 먼 픽셀을 같은 픽셀로 인식함) 
        # 픽셀간 거리 d > sigma_space인 경우, 픽셀 간 가중치는 0이 됨
        param_desc_sigma_color = ParameterDescriptor(
            description="Bilateral Filter의 sigma_color 파라미터",
            integer_range=[IntegerRange(from_value=1, to_value=100, step=1)]
        )
        param_desc_sigma_space = ParameterDescriptor(
            description="Bilateral Filter의 sigma_space 파라미터",
            integer_range=[IntegerRange(from_value=1, to_value=25, step=1)]
        )

        self.declare_parameter('sigma_color', 20, param_desc_sigma_color)
        self.declare_parameter('sigma_space', 5, param_desc_sigma_space)

        sigma_color = self.get_parameter('sigma_color').value
        sigma_space = self.get_parameter('sigma_space').value

        self.get_logger().info(f'sigma_color 초기값: {sigma_color}')
        self.get_logger().info(f'sigma_space 초기값: {sigma_space}')

        #4. Add on_set_parameters_callback 등록
        self.add_on_set_parameters_callback(self.para_callback)

        #5. cv_bridge 생성
        self.bridge1 = CvBridge()

    # 파라미터 변경 시 실행할 콜백: 변경 내용 출력
    def para_callback(self, params):
        for param in params:
            msg = f"{param.name}의 변경된 값: {param.value}"
            self.get_logger().info(msg)
        return SetParametersResult(successful=True)
    
    # 카툰 스타일 변환 후 이미지 발행
    def img_callback(self, msg):
        # 파라미터 값 받아오기
        sigma_color = self.get_parameter('sigma_color').value
        sigma_space = self.get_parameter('sigma_space').value

        # ROS img -> OpenCV img(BGR)
        cv_img = self.bridge1.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        bilateral = cv2.bilateralFilter(cv_img, d=-1, sigmaColor=sigma_color, sigmaSpace=sigma_space)
        edges = 255 - cv2.Canny(cv_img, 80, 120)
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        cartoon_img = cv2.bitwise_and(bilateral, edges)

        # OpenCV img -> ROS img
        cartoon_msg = self.bridge1.cv2_to_imgmsg(cartoon_img, encoding='bgr8')

        # ROS img 발행
        self.pubber.publish(cartoon_msg)

def main(args=None):
    rclpy.init(args=args)
    
    node1 = CartoonPub1()
    rclpy.spin(node1)

    node1.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()