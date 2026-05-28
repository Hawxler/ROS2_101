# 노드 1개, 도메인 ID 2개, 멀티프로세싱으로 토픽 발행
#다른 도메인에 있는 터틀심 조종하기
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import multiprocessing

class ControlOtherTurtles(Node):
    def __init__(self, domain_id: int, angular_speed: float):
        super().__init__(f'turtle_controller_node{domain_id}')

        # 터틀 제어를 위한 cmd_vel 퍼블리셔 생성
        self.pubber = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)
        self.angular_speed = angular_speed
        self.domain_id = domain_id

        # 1 pub per sec
        self.timer = self.create_timer(1.0, self.timer_callback)

    def timer_callback(self):
        msg = Twist()

        # 각속도는 지정된 값(양수: 반시계, 음수: 시계)으로 설정
        msg.linear.x = 2.0
        msg.angular.z = self.angular_speed

        # 발행
        self.pubber.publish(msg)

        direction = "반시계방향" if self.angular_speed > 0 else "시계방향"
        self.get_logger().info(
            f"[도메인{self.domain_id}] 방향: {direction}, 각속도: {msg.angular.z}"
        )

# 멀티프로세싱이 실행할 타겟 함수
def turtle_process(domain_id: int, angular_speed: float):
    # 각 프로세스에서 해당 도메인으로 rclpy 초기화
    rclpy.init(args=[], domain_id=domain_id)
    
    node1 = ControlOtherTurtles(domain_id, angular_speed)
    try:
        rclpy.spin(node1)
    except KeyboardInterrupt:
        pass
    finally:
        node1.destroy_node()
        rclpy.shutdown()

def main():
    # domain 1: 시계방향 (angular_speed < 0)
    p1 = multiprocessing.Process(target=turtle_process, args=(1, -1.0))
    # domain 2: 반시계방향 (angular_speed > 0)
    p2 = multiprocessing.Process(target=turtle_process, args=(2, 1.0))

    p1.start()
    p2.start()

    p1.join()
    p2.join()

if __name__ == '__main__':
    main()