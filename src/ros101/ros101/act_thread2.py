import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer

# 액션 서버 노드, pose 구독 노드 동시 실행용 쓰레드
from rclpy.executors import MultiThreadedExecutor

# 터틀심 메시지 타입: x, y, theta, linear_velocity, angular_velocity
from turtlesim.msg import Pose
# cmd_vel 속도 명령 메시지 타입: linear.x, angular.z
from geometry_msgs.msg import Twist 

# 내가 만든 인터페이스
# (MyAction1.Goal(), MyAction1.Result(), MyAction1.Feedback())
from interface_pkg1.action import MyAction1
###########################
# # Goal
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
############################
from ros101.subber0_2 import TurtleSubber0_2

import math
import time

# 액션/속도 발행
class DistSrvr3(Node):
    def __init__(self):
        super().__init__("act_srvr_node3")

        #1. 액션 서버 생성
        self.srvr_act3 = ActionServer(
            self,            # 현재 노드에 액션 서버 붙여라.
            MyAction1,       # 액션 타입
            'dist_action3',  # 액션명: $ ros2 action send_goal /dist_action3
            self.execute_callback # 터미널 클라가 goal 보내오면 실행 
        )

        #2. 거북이에게 속도 명령 발행
        self.pubber3 = self.create_publisher(
            Twist, 
            '/turtle1/cmd_vel', 
            10
        )

        self.total_dist = 0.0
        self.is_first_time = True # 처음이면 현재 위치를 이전 위치에 대입
        self.current_pose = Pose()
        self.previous_pose = Pose()
    
    def calc_diff_pose(self):
        if self.is_first_time:
            self.previous_pose.x = self.current_pose.x
            self.previous_pose.y = self.current_pose.y
            self.is_first_time = False
        
        diff_pose = math.sqrt(
            (self.current_pose.x - self.previous_pose.x)**2 + \
            (self.current_pose.y - self.previous_pose.y)**2
        )
        
        self.previous_pose = self.current_pose

        return diff_pose

    # 3. 액션 실행 콜백 (터미널 클라가 goal을 보내오면 실행)
    # 터미널에 입력한 요청값 "{linear_x: 2.0, angular_z: 1.0, dist: 40.0}"
    # goal_handle.request <- 터미널 클라가 보내온 goal 값
    # goal_handle.publish_feedback()
    # goal_handle.succeed()
    def execute_callback(self, goal_handle):
        feedback_msg = MyAction1.Feedback() # remaining_dist

        msg = Twist() # 거북이에게 보낼 속도 명령 cmd_vel 메시지 생성
        msg.linear.x = goal_handle.request.linear_x # 터미널 클라의 goal 값
        msg.angular.z = goal_handle.request.angular_z # 클라의 goal 값

        while True:
            self.total_dist += self.calc_diff_pose()
            feedback_msg.remaining_dist = goal_handle.request.dist - self.total_dist
            # print(f'남은 거리: {feedback_msg.remaining_dist:.2f}')
            goal_handle.publish_feedback(feedback_msg) # 터미널 클라 출력
            self.pubber3.publish(msg) #터틀심에게 속도 명령을 /turtle1/cmd_vel로 발행
            time.sleep(0.1)

            if feedback_msg.remaining_dist < 0.2:
                break
        
        goal_handle.succeed()
        result = MyAction1.Result() # 터미널 클라에게 보낼 결과 메시지 생성
        result.pose_x = self.current_pose.x
        result.pose_y = self.current_pose.y
        result.pose_theta = self.current_pose.theta
        result.result_dist = self.total_dist

        self.total_dist = 0.0
        self.is_first_time = True
        
        return result

# 4. 구속 노드 상속 클라스
# pose 구독한 값을 DistSrvr3.current_pose에 넣어줌.
# TurtleSubber0_2는 /turtle1/pose를 구독함.
class TurtleSub_Act(TurtleSubber0_2):
    def __init__(self, act_server): # act_server = DistSrvr3의 객체
        super().__init__()
        self._act_server = act_server #current_pose 갱신용
    
    def sub_callback(self, msg): # Overriding
        #부모 sub_callback()의 latest_pose 갱신
        super().sub_callback(msg) #또는 그냥 self.latest_pose = msg 라고 직접 수정해도 되기는 함.
        self._act_server.current_pose = msg #msg.x, msg.y, msg 세타

def main(args=None):
    rclpy.init(args=args)

    # 멀티스레드 executor 생성: 노드 두 개(node_act, node_sub) 있음
    # 즉, 액션 실행 중에도 pose 구독 콜백 계속 실행
    executor = MultiThreadedExecutor()
    node_act = DistSrvr3()    # 액션 서버 노드 생성
    node_sub = TurtleSub_Act(act_server=node_act) #pose 구독 노드 생성

    executor.add_node(node_act) # executor에 액션 서버 노드 등록
    executor.add_node(node_sub) # executor에 pose 구독 노드 등록

    try:
        executor.spin()
    finally:
        executor.shutdown()
        node_act.destroy_node()
        node_sub.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()