# 노드 1개, 도메인 ID 2개, 멀티프로세싱으로 Action 실행
# 액션:TeleportAbsolute: 터틀 하나는 왼쪽, 다른 하나는 오른쪽 이동
import rclpy
from rclpy.node import Node
import multiprocessing
import math
from rclpy.action import ActionClient
from turtlesim.action import RotateAbsolute

class TurtleActor(Node):
    def __init__(self, domain_id: int, target_theta_deg: float):
        super().__init__(f'tur_rotate_node{domain_id}')
        
        self.domain_id = domain_id
        self.target_theta = math.radians(target_theta_deg)

        # rotate_absolute 액션 클라 생성
        self.act_cli = ActionClient(self, RotateAbsolute, '/turtle/rotate_absolute')
    
    def send_goal1(self):
        # 액션 서버 준비 대기
        if not self.act_cli.wait_for_server(timeout_sec=5.0):
            self.get_logger().error("RotateAbsolute 액션 서버 준비 안 됨")
            return
        
        # 목표 각도 등 Goal 메시지 생성
        goal_msg = RotateAbsolute.Goal()
        goal_msg.theta = self.target_theta
        
        # 액션 서버에 목표 전송
        future = self.act_cli.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self, future)
        goal_handle = future.result()

        self.get_logger().info(
            f"[도메인{self.domain_id}] {self.target_theta:.2f} 회전 goal 전송"
            f"({math.degrees(self.target_theta):.1f} degrees)"
        )

        if not goal_handle.accepted:
            self.get_logger().error("Goal 거절됨")
            return
        
        self.get_logger().info("Goal 수락됨. 결과 대기 중...")

        # 결과를 기다림
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        result = result_future.result().result
        self.get_logger().info(f"[도메인{self.domain_id}] RotateAbsolute 액션 결과: {result}")

# 멀티프로세스가 실행할 타겟함수
def rotate_process(domain_id: int, target_theta_def: float):
    # 각 프로세스에서 해당 도메인으로 rclpy 초기화
    rclpy.init(args=[], domain_id=domain_id)

    node1 = TurtleActor(domain_id, target_theta_def)
    node1.send_goal1()
    
    node1.destroy_node()
    rclpy.shutdown()

def main():
    # Domain 1: turtle1을 90도로 회전
    p1 = multiprocessing.Process(target=rotate_process, args=(1, 90.0))
    # Domain 2: turtle1을 270도로 회전
    p2 = multiprocessing.Process(target=rotate_process, args=(2, 270.0))

    p1.start()
    p2.start()

    p1.join()
    p2.join()

if __name__ == '__main__':
    main()