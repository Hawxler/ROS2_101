# img_pub2.py + config에 parameter 추가
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class ImgPublisher3(Node):
    def __init__(self):
        super().__init__('img_pub_node3')

        #1. 디폴트 파라미터 설정 -> 실제 파라미터 불러오기
        self.declare_parameter('width', 640)
        self.width = self.get_parameter('width').value
        self.declare_parameter('height', 480)
        self.height = self.get_parameter('height').value
        self.declare_parameter('camera_device', 0)
        self.camera_device = self.get_parameter('camera_device').value
        self.declare_parameter('frame_rate', 480)
        self.frame_rate = self.get_parameter('frame_rate').value

        #2. 발행
        self.pubber = self.create_publisher(Image, '/image_raw', 10)
        time_period = 1.0 / self.frame_rate
        self.timer = self.create_timer(time_period, self.timer_callback)

        #3. CV 이미지 -> ROS 이미지
        self.cap = cv2.VideoCapture(self.camera_device)
        self.bridge1 = CvBridge()

        # if not self.cap.isOpened():
        #     self.get_logger().error(f'카메라 열기 실패: {self.camera_device}')
        # else:
        #     self.get_logger().info(f'카메라 열기 성공: {self.camera_device}')
        
        #4. 출력해서 확인해보기
        self.get_logger().info("Frame Width: " + str(self.width))
        self.get_logger().info("Frame Height: " + str(self.height))
        self.get_logger().info("Cam No: " + str(self.camera_device))
        self.get_logger().info("Frame Rate: " + str(self.frame_rate))

    def timer_callback(self):
        # self.get_logger().info('타이머 콜백 실행')
        ret, frame = self.cap.read()

        if not ret:
            self.get_logger().warn("프레임 읽기 실패")
            return

        frame = cv2.resize(frame, (self.width, self.height))

        img = self.bridge1.cv2_to_imgmsg(frame, encoding='bgr8')
        self.pubber.publish(img)
        
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)

    node1 = ImgPublisher3()
    rclpy.spin(node1)

    node1.cap.release()
    cv2.destroyAllWindows()

    node1.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()