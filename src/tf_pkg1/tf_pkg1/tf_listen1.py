# child_frame의 TF 정보를 구독하여 출력하는 노드 예제
# TF Tree 안에서 world → child1_frame 변환 정보를 조회한 뒤, child1_link가 world 원점에서 얼마나 떨어져 있는지 계산해서 dist_topic1 토픽으로 발행하는 노드
import math
import rclpy
from rclpy.node import Node

import tf2_ros
from std_msgs.msg import Float32

class ChildTfPubListener(Node):
    def __init__(self):
        super().__init__('tf_listener_node1')
        self.get_logger().info("TF Pub & Listener 노드 시작")

        #1. TF를 조회하기 위한 버퍼와 리스터 생성
        # /tf, /tf_static 토픽에서 발행되는 TF 정보를 버퍼에 저장하는 리스너 생성
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        #2. 원점으로부터의 거리를 발행하는 퍼블리셔 생성
        self.dist_pubber = self.create_publisher(Float32, 'dist_topic1', 10)

        #3. 타이머 설정 (0.1초마다 콜백 함수 호출)
        timer_period = 0.1 # seconds
        self.timer1 = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        try:
            #4. TF 정보 조회(예: 'base_link'에서 'child1_frame'까지의 변환 정보)
            # lookup_transform(부모, 자식, 시간)
            transform1 = self.tf_buffer.lookup_transform(
                'world',           # 기준(부모) 프레임
                'child1_frame',    # 찾을(자식) 프레임
                rclpy.time.Time()  # 최신 TF 정보 조회
            )

            #5. 조회한 TF 정보에서 위치 정보 추출
            x = transform1.transform.translation.x
            y = transform1.transform.translation.y
            z = transform1.transform.translation.z

            #6. 원점으로부터의 거리 계산(유클리드 거리)
            dist = math.sqrt(x**2 + y**2 + z**2)

            #7. 계산한 거리 정보를 Float32 메시지로 발행
            dist_msg = Float32()
            dist_msg.data = dist
            self.dist_pubber.publish(dist_msg)

        except Exception as e:
            # 아직 TF 정보가 수신되지 않았거나 조회(lookup)에 실패한 경우 예외 처리
            self.get_logger().warn(f"TF 정보 조회 실패: {e}")

def main(args=None):
    rclpy.init(args=args)

    node1 = ChildTfPubListener()
    rclpy.spin(node1)

    node1.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()