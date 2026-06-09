import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist

class TurtleCon1(Node):
    def __init__(self):
        super().__init__('p_con_node1')

        #1. 목표 위치, 허용 오차, 비례 상수 설정
        self.goal_x = 8.0
        self.tolerance = 0.05
        self.kp = 1.0

        #2. pose 변수 초기화
        self.pose = None

        #3. 구독자, 발행자, 타이머 설정
        self.subber = self.create_subscription(
            Pose, 
            '/turtle1/pose', 
            self.pose_callback, 
            10
        )

        self.pubber = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        self.timer = self.create_timer(0.05, self.timer_callback)

    #4. pose를 업데이트하는 콜백 함수
    def pose_callback(self, msg):
        self.pose = msg

    #5. 목표 위치까지의 거리(diff_x)를 계산하여 명령 속도를 발행
    def timer_callback(self):
        if self.pose is None:
            return
        
        diff_x = self.goal_x - self.pose.x

        twist = Twist()

        if abs(diff_x) > self.tolerance:
            # [P 제어] PID 제어에서 P 제어만 사용하여,
            # 목표 위치까지의 거리에 비례하여 명령 속도 계산
            twist.linear.x = self.kp * diff_x
            self.get_logger().info(
                f"현재 x: {self.pose.x:.2f}, 남은 거리: {diff_x:.2f}, 명령 속도: {twist.linear.x:.2f}"
            )
        else:
            twist.linear.x = self.kp * 0.0
            self.get_logger().info("도착")
        
        self.pubber.publish(twist)

def main(args=None):
    rclpy.init(args=args)

    node1 = TurtleCon1()
    rclpy.spin(node1)

    node1.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()