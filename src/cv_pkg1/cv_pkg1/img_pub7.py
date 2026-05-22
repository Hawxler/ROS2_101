# Optical Flow: 픽셀 이동 추정
# 움직임 계산 > /image_optical_vector 토픽 발행 > 원본 이미지에 벡터 화살표로 표시
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class OpticalFlowPub(Node):
    def __init__(self):
        super().__init__('optical_flow_pub_node1')
        self.get_logger().info("Optical Flow 노드 시작")

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
            '/image_optical_vector',
            10
        )

        #3. cv_bridge 생성
        self.bridge1 = CvBridge()
        self.prev_gray = None # 이전 프레임의 그레이스케일 이미지 저장

    # 이미지 콜백 함수
    def img_callback(self, msg):
        #1. ROS img > OpenCV img > 그레이스케일 변환
        current_frame = self.bridge1.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        current_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)

        #2. 첫 프레임은 이전 프레임이 그냥 저장(초기화)하고 리턴
        if self.prev_gray is None:
            self.prev_gray = current_gray
            return
        
        #3. Optical Flow 계산(Farneback 방법 사용)
        flow = cv2.calcOpticalFlowFarneback(
            self.prev_gray, 
            current_gray,
            None,
            0.5,   # pitch yaw roll 범위 > 이미지 피라미드에서 각 레벨의 크기 비율
            3,     # pyramid levels
            15,    # window size
            3,     # iterations
            5,     # poly_n
            1.2,   # poly_sigma
            0      # flags
        )

        #4. Optical Flow 벡터를 원본 이미지에 화살표로 표시
        # draw_flow_vectors 함수 작성하여 flow 벡터를 이미지에 그리기 (예: cv2.arrowedLine 사용). flow 벡터는 (dx, dy) 형태로 저장되어 있음.
        flow_vec_img = current_frame.copy()
        self.draw_flow_vectors(flow_vec_img, flow, step=16) # step은 벡터를 그릴 간격
        flow_vec_msg = self.bridge1.cv2_to_imgmsg(flow_vec_img, encoding='bgr8')
        flow_vec_msg.header = msg.header # 원본 이미지 메시지의 헤더를 복사하여 타임스탬프와 프레임 아이디 유지
        self.pubber.publish(flow_vec_msg)

        #5. 현재 프레임을 이전 프레임으로 저장
        self.prev_gray = current_gray

    def draw_flow_vectors(self, frame, flow, step=16):
        h, w = frame.shape[:2]
        for y in range(0, h, step):
            for x in range(0, w, step):
                # flow[y, x]는 (dx, dy) 형태로 저장되어 있음
                dx, dy = flow[y, x]
                end_x = int(x + dx) # 화살표의 끝 좌표 계산. 변화가 크면 화살표가 길어짐
                end_y = int(y + dy)
                # 화살표 그리기: 시작점 (x, y)에서 끝점 (end_x, end_y)로 화살표를 그림. 색상은 초록색, 두께는 1, 선 유형은 cv2.LINE_AA로 설정하여 부드러운 선을 그림
                cv2.arrowedLine(
                    frame, (x, y), 
                    (end_x, end_y), 
                    color=(0, 255, 0), 
                    thickness=1, 
                    tipLength=0.4,
                    line_type=cv2.LINE_AA
                )

def main(args=None):
    rclpy.init(args=args)

    node1 = OpticalFlowPub()
    rclpy.spin(node1)

    node1.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()