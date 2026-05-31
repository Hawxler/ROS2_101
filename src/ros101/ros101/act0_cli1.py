import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from interface_pkg1.action import MyAction1

class ActCli1(Node):
    def __init__(self):
        super().__init__('act_cli_node1')

        self.action_client = ActionClient(
            self,
            MyAction1,
            'dist_act1' # 액션 이름. 서버 액션명과 동일해야 함.
        )

    # req를 보냄
    def send_goal(self):
        #1. goal 만들기
        goal_msg = MyAction1.Goal()
        goal_msg.linear_x = 2.0
        goal_msg.angular_z = 1.0
        goal_msg.dist = 5.0

        # 서버 준비 대기
        self.action_client.wait_for_server()

        self.get_logger().info("Goal 전송")

        #2. 요청/서버 수락 응답용 future/피드백 콜백
        # (1) goal_msg 비동기로 보내기
        # (2) 서버의 수락/거부 받을 future 생성
        # (3) 서버가 feedback을 보내면 실행할 콜백을 등록함.
        self.send_goal_future = self.action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback   
        )

        #3. 서버 수락 goal_future가 완료(done)되면 실행할 콜백
        # 즉, 서버가 Goal 수락/거부 응답을 보내오면 실행할 콜백
        self.send_goal_future.add_done_callback(
            self.goal_response_callback
        )

    #4. [2-2] 서버로부터 수락/거부 응답 수신 시 실행
    # 수락 응답(goal_future)으로 goal_handle 생성
    def goal_response_callback(self, future):
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().info("Goal 거절됨.")
            return
        
        self.get_logger().info("Goal 수락됨")

        #5. result_future: 서버가 최종 결과를 보내올 때까지 비동기로 대기 
        self.get_result_future = goal_handle.get_result_async()
        
        #6. result 수신 시 실행할 콜백 추가(지정)
        self.get_result_future.add_done_callback(
            self.get_result_callback
        )
    
    #7. [2-3] 서버로부터 진행 상황 피드백 수신 시 실행
    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(
            f'[피드백] 잔여 거리: {feedback.remaining_dist:.2f}'
        )

    #8. [6-] 서버로부터 결과(result_future) 수신 시 실행
    def get_result_callback(self, future):
        result = future.result().result

        self.get_logger().info(
            f'Result: Pose_x={result.pose_x:.2f}, '
            f'pose_y={result.pose_y:.2f}, '
            f'pose_theta={result.pose_theta:.2f}, '
            f'result_dist={result.result_dist:.2f}'
        )

        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)

    node1 = ActCli1()
    node1.send_goal()

    rclpy.spin(node1)

if __name__ == '__main__':
    main()