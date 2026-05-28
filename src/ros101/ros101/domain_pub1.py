# 노드 1개, 도메인 ID 2개, 멀티프로세싱으로 토픽 발행
# 다른 터미널 2곳에서 같은 토픽 구독:
# $ export ROS_DOMAIN_ID=1 또는 2 
# $ ros2 topic echo /domain_test_topic1 
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
import multiprocessing

class DomainPub1(Node):
    def __init__(self, domain_id: int, start_value: int, increment: int):
        super().__init__(f"domain_pub_node{domain_id}")
        
        self.pubber = self.create_publisher(Int32, 'id_test_topic1', 10)

        self.value = start_value
        self.increment = increment
        self.domain_id = domain_id

        self.timer = self.create_timer(1.0, self.timer_callback) # 1 sec

    def timer_callback(self):
        msg = Int32()
        msg.data = self.value
        self.pubber.publish(msg)

        self.get_logger().info(f"도메인 {self.domain_id}, 발행: {msg.data}")
        self.value += self.increment

# 멀티프로세싱이 실행할 타겟 함수
def pub_process(domain_id: int, start_value: int, increment: int):
    # 각 프로세스에서 각자 도메인으로 rclpy 초기화
    rclpy.init(args=[], domain_id=domain_id)
    
    node1 = DomainPub1(domain_id, start_value, increment)
    try:
        rclpy.spin(node1)
    except KeyboardInterrupt:
        pass

    node1.destroy_node()
    rclpy.shutdown()

def main():
    # domain 1: 1부터 2씩 증가(domain_id=1, start_val=1, inc=2)
    p1 = multiprocessing.Process(target=pub_process, args=(1, 1, 2))
    # domain 2: 2부터 2씩 증가(2, 2, 2)
    p2 = multiprocessing.Process(target=pub_process, args=(2, 2, 2))

    p1.start() # p1 시작
    p2.start() # p2 시작

    p1.join()  # p1이 끝날 때까지 대기
    p2.join()  # p2가 끝날 때까지 대기

if __name__ == '__main__':
    main()