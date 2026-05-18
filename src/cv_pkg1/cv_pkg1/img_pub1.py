# ros2 run usb_cam usb_cam_node_exe 대신 퍼블리셔로 실행하기
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class ImgPubber1(Node):
    def __init__(self):
        super().__init__('img_pub_node1')

        # '/image_raw' 발행
        self.pubber = self.create_publisher(Image, '/image_raw', 10)
        time_period = 1.0 / 30.0 # 30 FPS이므로 30Hz로 권장!
        self.timer = self.create_timer(time_period, self.timer_callback)
        
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.get_logger().error("카메라 열기 실패")

        self.cv_bridge = CvBridge()

    def timer_callback(self):
        ret, frame = self.cap.read()
        if not ret or frame is None:
            self.get_logger().warn("프레임 읽기 실패")
            return
        
        # cv_bridge: cv 이미지를 ros 이미지로 변환
        img = self.cv_bridge.cv2_to_imgmsg(frame, 'bgr8')
        self.pubber.publish(img)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)

    node1 = ImgPubber1()
    rclpy.spin(node1)
    node1.destroy_node()
    rclpy.shutdown()

if __name__=='__main__':
    main()