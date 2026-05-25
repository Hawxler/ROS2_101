#tf_b1 + Quternion 계산 추가 버전
import math
import rclpy
from rclpy.node import Node

from geometry_msgs.msg import TransformStamped
import tf2_ros
from tf_transformations import quaternion_from_euler

class MyTfBroadcaster2(Node):
    def __init__(self):
        super().__init__('tf_broadcaster_node2')
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
        # 각도 조금씩 증가 (0.1 라디안씩)
        self.angle += 0.1

        #8. 쿼터니언 구하기
        #8.1 반지름 2.0m인 원형 궤적(x=2.0*cos(angle), y=2.0*sin(angle))
        r = 2.0
        x = r * math.cos(self.angle)
        y = r * math.sin(self.angle)
        z = 0.0

        #8.2 원의 중심(0,0)을 바라보도록 yaw 회전 각도 계산 (z축 회전)
        # (x, y)에서 원점(0,0)을 바라보는 방향의 yaw 각도
        # 즉, (x, y) 입장에서 원점은 (-x, -y)이므로 atan2(-y, -x)로 계산
        yaw = math.atan2(-y, -x)

        #8.3 오일러 각 -> 쿼터니언 변환 (roll=0, pitch=0, yaw)
        q = quaternion_from_euler(0, 0, yaw)

        #9. 위치 변환 정보 입력
        tf_stamped.transform.translation.x = x
        tf_stamped.transform.translation.y = y
        tf_stamped.transform.translation.z = z

        #10. 자세 변환 회전 정보 입력 (계산된 쿼터니언)
        tf_stamped.transform.rotation.x = q[0]
        tf_stamped.transform.rotation.y = q[1]
        tf_stamped.transform.rotation.z = q[2]
        tf_stamped.transform.rotation.w = q[3]

        #11. TF 발행
        self.br1.sendTransform(tf_stamped)

def main(args=None):
    rclpy.init(args=args)

    node1 = MyTfBroadcaster2()
    rclpy.spin(node1)

    node1.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()