# Launch + param_file로 실행하기(cv2.launch.py)
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class ImgPublisher2(Node):
    def __init__(self):
        super().__init__('img_pub_node2')

        # 1. 발행
        self.pubber = self.create_publisher(Image, '/image_raw', 10)

        time_period = 0.01
        self.timer = self.create_timer(time_period, self.timer_callback)

        # 2. 이미지 캡쳐 및 변환
        self.cap = cv2.VideoCapture(0)
        self.bridge1 = CvBridge()

        # 3. 파라미터 디폴드값(640,480) 설정 -> 원하는 파라미터값(320, 240) 불러와 출력하기
        self.declare_parameter('width', 640)
        self.width = self.get_parameter('width').value
        self.declare_parameter('height', 480)
        self.height = self.get_parameter('height').value
        output_msg = "Frame Width: " + str(self.width) + "\t"
        output_msg = output_msg + "Frame Height: " + str(self.height)
        self.get_logger().info(output_msg)
    
    def timer_callback(self):
        ret, frame = self.cap.read()
        if ret:
            ros_img_msg = self.bridge1.cv2_to_imgmsg(frame, encoding='bgr8')
            self.pubber.publish(ros_img_msg)
            self.get_logger().info('카메라 이미지 발행 중')
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)

    node1 = ImgPublisher2()
    rclpy.spin(node1)

    node1.cap.release()
    cv2.destroyAllWindows()

    node1.destroy_node()
    rclpy.shutdown()

if __name__=='__main__':
    main()