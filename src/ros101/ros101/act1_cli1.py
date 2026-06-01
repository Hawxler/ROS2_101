# 서버에게 “linear_x=2.0, angular_z=1.0으로 10바퀴 돌아라”는 Goal을 보낸다.
# 서버가 보내는 feedback을 받는다.
# 서버가 최종 result를 보내면 출력하고 종료한다.
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from interface_pkg1.action import MyAction2

class CircleActionClient(Node):
    def __init__(self):
        super().__init__('act_circle_cli_node1')

        self.act_cli = ActionClient(
            self,
            MyAction2,
            'circle_act1'
        )

    def send_goal(self):
        #1. Goal 메시지 생성
        goal_msg = MyAction2.Goal()
        goal_msg.linear_x = 2.0
        goal_msg.angular_z = 1.0
        goal_msg.laps = 10.0
        
        #2. 액션 서버가 준비될 때까지 대기
        self.act_cli.wait_for_server()
        self.get_logger().info("10바퀴 goal 전송")

        #3. Goal 메시지 전송 + feedback 수신 대기
        # 서버의 수락/거부 응답을 위한 future 객체 리턴받아 저장
        self.send_goal_future = self.act_cli.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )

        #4. send_goal_future가 완료되면(서버가 Goal 수락/거부 응답하면) 실행할 콜백(goal_response_callback()) 등록
        self.send_goal_future.add_done_callback(
            self.goal_response_callback
        )
    
    #5. 서버가 Goal 수락/거부 응답하면 실행되는 콜백 함수
    def goal_response_callback(self, future):
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().info("Goal 거부됨")
            return
        
        self.get_logger().info("Goal 수락됨")

        self.get_result_future = goal_handle.get_result_async()
        self.get_result_future.add_done_callback(
            self.get_result_callback
        )
    
    #6. 서버가 Goal 수락 후, feedback 메시지 받을 때마다 실행되는 콜백 함수
    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(
            f'남은 회전 수: {feedback.remaining_laps:.2f}'
        )
    
    #7. 서버가 최종 future(status + result) 메시지 보낼 때 실행되는 콜백 함수
    def get_result_callback(self, future):
        result = future.result().result

        self.get_logger().info(
            f'Result: x={result.pose_x:.2f}, '
            f'y={result.pose_y:.2f}, '
            f'theta={result.pose_theta:.2f}, '
            f'completed_laps={result.result_laps:.2f}'
        )

        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)

    node1 = CircleActionClient()
    node1.send_goal()

    try:
        rclpy.spin(node1)
    finally:
        node1.destroy_node()


if __name__ == '__main__':
    main()