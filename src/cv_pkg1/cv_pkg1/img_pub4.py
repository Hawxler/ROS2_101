# 이미지 색변환기: 파라미터로 HSV 색 변환해서 출력하기
# img_pub3가 발행하는 /image_raw 구독해서 -> 색변환해서 -> /image_hsv 발행하기
# 상세 절차: /image_raw 구독 -> cv_bridge로 ROS 이미지를 OpenCV 이미지로 변환 -> cv2.cvtColor로 BGR을 HSV로 변환 -> S, V 채널 보정 색변환 (파라미터 설정) -> 변환 후 cv2.cvtColor로 HSV를 BGR로 변환 -> cv_bridge로 OpenCV 이미지를 ROS 이미지로 변환 -> /image_hsv 발행 
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np
from rcl_interfaces.msg import ParameterDescriptor, FloatingPointRange, SetParametersResult

class HSVconverter(Node):
    def __init__(self):
        super().__init__('img_pub_node4')
        self.get_logger().info("HSV Converter 시작")

        #1. 이미지 구독자 생성 (/image_raw4 구독)
        self.subber = self.create_subscription(
            Image,
            '/image_raw', 
            self.image_callback,
            10
        )

        #2. 이미지 발행자 생성
        self.pubber = self.create_publisher(
            Image,
            '/image_hsv',
            10
        )

        #3. OpenCV img <-> ROS img
        self.bridge1 = CvBridge()

        #4. 트랙바로 조정할 파라미터의 설명 추가
        # FloatingPointRange(최솟값, 최댓값, 조정 단위)
        param_desc_sat_scale = ParameterDescriptor(
            description='Saturation Scale Factor',
            floating_point_range = [FloatingPointRange(from_value=0.0, to_value=2.0, step=0.01)],
        )
        param_desc_val_scale = ParameterDescriptor(
            description='Value Scale Factor',
            floating_point_range = [FloatingPointRange(from_value=0.0, to_value=2.0, step=0.01)],
        )

        #5. 트랙바로 조정할 파라미터 선언(초기값 1.0) 및 현재값
        # S_scale: 채도 스캐일, V_scale: 명도 스케일
        self.declare_parameter('S_scale', 1.0, param_desc_sat_scale)
        self.declare_parameter('V_scale', 1.0, param_desc_val_scale)

        sat_scale = self.get_parameter('S_scale').value
        val_scale = self.get_parameter('V_scale').value

        output_msg = f"채도 스케일: {sat_scale}, 명도 스케일: {val_scale}"
        self.get_logger().info(output_msg)

        self.add_on_set_parameters_callback(self.parameter_callback)

    def parameter_callback(self, params):
        for param in params:
            msg = param.name + '이 변경됨. 변경 후: ' + str(param.value)
            self.get_logger().info(msg)

        return SetParametersResult(successful=True)
    
    def image_callback(self, msg):
        # 트랙바로 설정한 파라미터값 읽기
        sat_scale = self.get_parameter('S_scale').value
        val_scale = self.get_parameter('V_scale').value

        # ROS img -> OpenCV img
        cv_img = self.bridge1.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # BGR -> HSV
        hsv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)
        H, S, V = cv2.split(hsv_img)

        # S, V 채널 보정(정수형으로 변환 + 스케일 적용)
        S = np.clip(S * sat_scale, 0, 255).astype(np.uint8)
        V = np.clip(V * val_scale, 0, 255)
        V = np.uint8(V) # 위처럼 astype(np.uint8)로 해도 되지만 연습으로.
        hsv_img = cv2.merge((H, S, V))

        # HSV -> BGR
        result_img = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2BGR)
        hsv_msg = self.bridge1.cv2_to_imgmsg(result_img, encoding='bgr8')

        # /image_hsv 발행
        self.pubber.publish(hsv_msg)

def main():
    rclpy.init()

    node1 = HSVconverter()
    rclpy.spin(node1)

    node1.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
