# TF 브로드캐스터 노드 예제: 자식 프레임이 부모로부터 r만큼 떨어진 원형 궤적을 그리도록 변환 정보 발행
import math
import rclpy
from rclpy.node import Node

from geometry_msgs.msg import TransformStamped
import tf2_ros

class MyTfBroadcaster(Node):
    def __init__(self):
        super().__init__('tf_broadcaster_node1')
        self.get_logger().info("TF Broadcaster 노드 시작")

        #1. TF 브로드캐스터 생성
        self.br1 = tf2_ros.TransformBroadcaster(self)

        #2. 타이머 설정 (0.1초마다 콜백 함수 호출)
        timer_period = 0.1  # seconds
        self.timer1 = self.create_timer(timer_period, self.timer_callback)

        #3. 각도 변수 초기화
        self.angle = 0.0

    def timer_callback(self):
        #4. TransformStamped 메시지 생성
        tf_stamped = TransformStamped()

        #5. 시간 정보 입력
        tf_stamped.header.stamp = self.get_clock().now().to_msg()

        #6. 부모/자식 프레임 지정
        tf_stamped.header.frame_id = 'world'
        tf_stamped.child_frame_id = 'base_link'

        #7. 각도를 조금씩 증가시키면서 원형 궤적을 그리도록 변환 정보 입력 (예: x=cos(angle), y=sin(angle), z=0.0, 회전은 단위 쿼터니언)
        # 각도 조금씩 증가 (0.01 라디안씩)
        self.angle += 0.01 

        # 반지름 2.0m인 원형 궤적(x=2.0*cos(angle), y=2.0*sin(angle))
        r = 2.0
        x = r * math.cos(self.angle)
        y = r * math.sin(self.angle)
        z = 0.0

        #8. 위치 변환 정보 입력
        tf_stamped.transform.translation.x = x
        tf_stamped.transform.translation.y = y
        tf_stamped.transform.translation.z = z

        #9. 자세 변환 회전 정보 입력 (단위 쿼터니언(회전 없음): x=0.0, y=0.0, z=0.0, w=1.0)
        # 회전 없으므로 안 써줘도 되지만, 그냥 명시적으로 입력해둠.
        tf_stamped.transform.rotation.x = 0.0
        tf_stamped.transform.rotation.y = 0.0
        tf_stamped.transform.rotation.z = 0.0
        tf_stamped.transform.rotation.w = 1.0

        #10. TF 발행
        self.br1.sendTransform(tf_stamped)

def main(args=None):
    rclpy.init(args=args)

    node1 = MyTfBroadcaster()
    rclpy.spin(node1)

    node1.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
