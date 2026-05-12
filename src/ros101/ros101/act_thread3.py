# act_thread3.py + 파라미터 조작
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from rclpy.executors import MultiThreadedExecutor
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
from rcl_interfaces.msg import SetParametersResult

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

class DistSrvr4(Node):
    def __init__(self):
        super().__init__("act_srvr_node4")
        self.total_dist = 0.0
        self.is_first_time = True
        self.current_pose = Pose()
        self.previous_pose = Pose()

        # 파라미터 연습용 블록
        self.declare_parameter('quantile_time', 0.75)
        self.declare_parameter('near_goal_time', 0.95)
        quantile_time, near_goal_time = self.get_parameters(
            ['quantile_time', 'near_goal_time']
        )
        self.quantile_time = quantile_time.value
        self.near_goal_time = near_goal_time.value
        # print(f'quantile_time: {quantile_time.value}, near_goal_time: {near_goal_time.value}')
        self.add_on_set_parameters_callback(self.param_callback)

        #1. 액션 서버 생성
        self.srvr_act4 = ActionServer(
            self,
            MyAction1,
            'dist_action4',
            self.execute_callback
        )

        #2. 거북이에게 속도 명령 발행
        self.pubber3 = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )
    
    # 터미널에서 파라미터 변경하면 내용 출력
    # from rcl_interfaces.msg import SetParametersResult
    def param_callback(self, params):
        for param in params:
            print(param.name, "변경 후:", param.value)
            
            # 파이썬 코드에서도 변경 변수값 적용해두기
            if param.name == 'quantile_time':
                self.quantile_time = param.value
            if param.name == 'near_goal_time':
                self.near_goal_time = param.value
        
        print(f'[변경 적용] quantile_time: {self.quantile_time}, near_goal_time: {self.near_goal_time}')
        return SetParametersResult(successful=True) 

    def calc_diff_pose(self):
        if self.is_first_time:
            self.previous_pose.x = self.current_pose.x
            self.previous_pose.y = self.current_pose.y
            self.is_first_time = False

        diff_pose = math.sqrt(
            (self.current_pose.x - self.previous_pose.x)**2 +\
            (self.current_pose.y - self.previous_pose.y)**2
        )

        self.previous_pose = self.current_pose

        return diff_pose
    
    # 3. 액션 실행 콜백 (터미널 클라의 goal request를 받으면 실행)
    # 터미널에 입력한 요청값 "{linear_x: 2.0, angular_z: 1.0, dist: 40.0}"
    # goal_handle.request <- 터미널 클라가 보내온 goal 값
    # goal_handle.publish_feedback()
    # goal_handle.succeed()
    def execute_callback(self, goal_handle):
        self.get_logger().info("액션 서버 콜백 실행")
        feedback_msg = MyAction1.Feedback() # remaining_dist

        msg = Twist()
        msg.linear.x = goal_handle.request.linear_x
        msg.angular.z = goal_handle.request.angular_z

        while True:
            self.total_dist += self.calc_diff_pose()
            feedback_msg.remaining_dist = goal_handle.request.dist - self.total_dist
            self.get_logger().info(f'남은 거리: {feedback_msg.remaining_dist:.2f}')
            goal_handle.publish_feedback(feedback_msg)
            self.pubber3.publish(msg)
            
            time.sleep(0.1)

            if feedback_msg.remaining_dist < 0.2:
                self.get_logger().info("목표 거리 도달")
                break
            
        goal_handle.succeed()
        result = MyAction1.Result() # 결과값 to 터미널 클라
        result.pose_x = self.current_pose.x
        result.pose_y = self.current_pose.y
        result.pose_theta = self.current_pose.theta
        result.result_dist = self.total_dist

        self.total_dist = 0.0
        self.is_first_time = True

        return result

#4. 구독 노드를 상속하는 클래스
class TurtleSub_Act(TurtleSubber0_2):
    def __init__(self, act_server): #act_server는 DistSrvr4의 객체
        super().__init__()
        self.act_server = act_server #current_pose 갱신용
    
    def sub_callback(self, msg): #Overriding
        #부모 sub_callback의 latest_pose 갱신
        super().sub_callback(msg) #또는 self.latest_pose = msg 라고 직접 수정
        self.act_server.current_pose = msg #msg.x, msg.y, msg.theta

def main(args=None):
    rclpy.init(args=args)

    executor = MultiThreadedExecutor()
    node_act = DistSrvr4()
    node_sub = TurtleSub_Act(act_server=node_act)

    executor.add_node(node_act)
    executor.add_node(node_sub)

    try:
        executor.spin()
    finally:
        executor.shutdown()
        node_act.destroy_node()
        node_sub.destroy_node()
        rclpy.shutdown()

if __name__=='__main__':
    main()          
