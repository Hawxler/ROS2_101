# 액션 기본 서버
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer

from interface_pkg1.action import MyAction1
#################################################
# # Request
# float32 linear_x
# float32 angular_z
# float32 dist
# ---
# # Result
# float32 pose_x
# float32 pose_y
# float32 pose_theta
# float32 result_dist
# ---
# # Feedback
# float32 remaining_dist
################################################

class ActSrvr1(Node):
    def __init__(self):
        super().__init__('act_srvr_node1')

        #1. 서버 생성
        self.act_srvr = ActionServer(
            self,
            MyAction1,
            'dist_act1',  # 액션 이름
            self.execute_callback
        )

    #2. 서버 동작 규정: req 들어오면 수락하고 콜백 실행 > goal_handle로 req 처리 관리함.
    #######################################
    # goal_handle.request          # 클라이언트가 보낸 요청값
    # goal_handle.publish_feedback # 중간 피드백 전송
    # goal_handle.succeed()        # 성공 처리
    # goal_handle.abort()          # 실패 처리
    # goal_handle.canceled()       # 취소 처리
    #######################################
    def execute_callback(self, goal_handle):
        # 서버가 콜백을 실행할 때 자동으로 클라에게 수락 답변을 전송함.
        self.get_logger().info('Goal 수락함.')

        #1. 수신된 Goal 요청 내용 확인
        self.get_logger().info(
            f'수신한 linear_x={goal_handle.request.linear_x}, '
            f'수신한 angular_z={goal_handle.request.angular_z}, '
            f'수신한 dist={goal_handle.request.dist}'
        )
        
        #2. 피드백 생성
        # 원래는 (남은 거리 = 목표 거리 - 이동한 거리)이어야 함.
        feedback_msg = MyAction1.Feedback()
        feedback_msg.remaining_dist = goal_handle.request.dist
        # 클라에게 피드백 보내기
        goal_handle.publish_feedback(feedback_msg)

        #3. goal 상태를 그냥 성공으로 바꿈.
        goal_handle.succeed()

        #4. 요청 위치로 다 이동했다고 간주함.
        result = MyAction1.Result()
        result.pose_x = 0.0
        result.pose_y = 0.0
        result.pose_theta = 0.0
        result.result_dist = goal_handle.request.dist

        return result # 클라에게 result 보냄
    
def main(args=None):
    rclpy.init(args=args)

    node1 = ActSrvr1()
    rclpy.spin(node1)

    node1.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()