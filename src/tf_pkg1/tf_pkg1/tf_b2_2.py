# 한 파일에 Child frame 노드 통합하여 추가하기
import math
import rclpy
from rclpy.node import Node

from geometry_msgs.msg import TransformStamped
import tf2_ros
from tf_transformations import quaternion_from_euler

class CombinedBroadcater(Node):
    def __init__(self):
        super().__init__('combined_broadcaster_node')
        self.get_logger().info("Combined TF Broadcaster 노드 시작")

        #1. TF 브로드캐스터 생성
        self.br1 = tf2_ros.TransformBroadcaster(self)

        #2. 타이머 설정 (0.1초마다 콜백 함수 호출)
        timer_period = 0.1 # seconds
        self.timer1 = self.create_timer(timer_period, self.timer_callback)

        #3. 각도 변수 초기화
        self.angle = 0.0

    def send_tf(self, parent, child, x, y, z, yaw):
        #4. TransformStamped 메시지 생성
        tf_stamped = TransformStamped()

        #5. 시간 정보 입력
        tf_stamped.header.stamp = self.get_clock().now().to_msg()

        #6. 부모/자식 프레임 지정
        tf_stamped.header.frame_id = parent
        tf_stamped.child_frame_id = child
        
        #7. 위치 변환 정보 입력
        tf_stamped.transform.translation.x = x
        tf_stamped.transform.translation.y = y
        tf_stamped.transform.translation.z = z

        #8. 자세 변환 회전 정보 입력 (계산된 쿼터니언)
        q = quaternion_from_euler(0, 0, yaw)
        tf_stamped.transform.rotation.x = q[0]
        tf_stamped.transform.rotation.y = q[1]
        tf_stamped.transform.rotation.z = q[2]
        tf_stamped.transform.rotation.w = q[3]

        #9. TF 발행
        self.br1.sendTransform(tf_stamped)

    def timer_callback(self):
        #10. 각도를 조금씩 증가시키면서 원형 궤적을 그리도록 변환 정보 입력 (예: x=cos(angle), y=sin(angle), z=0.0, 회전은 단위 쿼터니언)
        # 각도 조금씩 증가 (0.1 라디안씩)
        self.angle += 0.1

        #11. 쿼터니언 구하기
        #반지름 2.0m인 원형 궤적(x=2.0*cos(angle), y=2.0*sin(angle))
        # world -> moving_frame TF 발행: 반지름 2.0m 원이 (0,0)을 바라보도록
        r1 = 2.0
        x1 = r1 * math.cos(self.angle)
        y1 = r1 * math.sin(self.angle)
        z1 = 0.0
        yaw1 = math.atan2(-y1, -x1)
        self.send_tf('world', 'moving_frame', x1, y1, z1, yaw1)

        # moving_frame -> child1_frame TF 발행: 반지름 1.0m 원이 2배 빠르게 moving_frame을 보며 회전
        r2 = 1.0
        angle2 = self.angle * 2  # moving_frame보다 2배 빠르게 회전
        x2 = r2 * math.cos(angle2)
        y2 = r2 * math.sin(angle2)
        z2 = 0.0
        yaw2 = math.atan2(-y2, -x2)
        self.send_tf('moving_frame', 'child1_frame', x2, y2, z2, yaw2)

def main(args=None):
    rclpy.init(args=args)

    node1 = CombinedBroadcater()
    rclpy.spin(node1)

    node1.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()