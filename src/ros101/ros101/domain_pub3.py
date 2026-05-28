# 노드 1개, 도메인 ID 2개, 멀티프로세싱으로 서비스 실행
# 서비스:TeleportAbsolute: 터틀 하나는 왼쪽, 다른 하나는 오른쪽 이동
import rclpy
from rclpy.node import Node
import multiprocessing
from turtlesim.srv import TeleportAbsolute

class TeleportMultiTurtles(Node):
    def __init__(self, domain_id: int, target_x: float):
        super().__init__(f'teleporter_node{domain_id}')
        self.domain_id = domain_id
        self.target_x = target_x

        # teleport_absolute 서비스 클라 생성
        self.tele_cli = self.create_client(TeleportAbsolute, '/turtle1/teleport_absolute')
    
    # 서비스 요청하고, 결과를 future에 담아두기
    def teleport_srvc_call(self):
        # 서비스 준비될 때까지 대기
        if not self.tele_cli.wait_for_service(timeout_sec=5.0):
            self.get_logger().error("Teleport 서비스 불가")
            return
        
        # 요청 메시지 구성(y, theta는 기본값 사용)
        req = TeleportAbsolute.Request()
        req.x = self.target_x
        req.y = 5.544   # 기본 y 좌표
        req.theta = 0.0
        self.get_logger().info(f"[도메인{self.domain_id}] 텔레포트 x좌표: {self.target_x}")
        
        # 서비스 호출 및 결과 대기
        future = self.tele_cli.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        try:
            future.result()
            self.get_logger().info(f"[도메인{self.domain_id}] 텔레포트 서비스 성공")
        except Exception as e:
            self.get_logger().error(f"텔레포트 실패: {e}")

# 멀티프로세싱이 실행할 타겟함수
def teleport_process(domain_id: int, target_x: float):
    # 각 프로세스에서 각자 도메인으로 rclpy 초기화
    rclpy.init(args=[], domain_id=domain_id)

    node1 = TeleportMultiTurtles(domain_id, target_x)
    node1.teleport_srvc_call()

    node1.destroy_node()
    rclpy.shutdown()

def main():
    # domain 1: x = 2로 텔레포트 (타겟함수, (도메인 id, x좌표))
    p1 = multiprocessing.Process(target=teleport_process, args=(1, 2.0))
    # domain2: x = 8로 텔레포트
    p2 = multiprocessing.Process(target=teleport_process, args=(2, 8.0))

    p1.start()
    p2.start()

    p1.join()
    p2.join()

if __name__ == '__main__':
    main()