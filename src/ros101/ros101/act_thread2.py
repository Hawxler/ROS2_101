import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from rclpy.executors import MultiThreadedExecutor

from turtlesim.msg import Pose
from geometry_msgs.msg import Twist

from interface_pkg1.action import MyAction1
from ros101.subber0_2 import TurtleSubber0_2

import math
import time

class DistSrvr3(Node):
    def __init__(self):
        super().__init__("act_srvr_node3")
        self.srvr_act3 = ActionServer(
            self, 
            MyAction1, 
            'dist_action3',
            self.execute_callback
        )

        self.pubber3 = self.create_publisher(
            Twist, 
            '/turtle1/cmd_vel', 
            10
        )

        self.total_dist = 0.0
        self.is_first_time = True
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

    def execute_callback(self, goal_handle):
        feedback_msg = MyAction1.Feedback()

        msg = Twist()
        msg.linear.x = goal_handle.request.linear_x
        msg.angular.z = goal_handle.request.angular_z

        while True:
            self.total_dist += self.calc_diff_pose()
            feedback_msg.remaining_dist = goal_handle.request.dist - self.total_dist
            # print(f'남은 거리: {feedback_msg.remaining_dist:.2f}')
            goal_handle.publish_feedback(feedback_msg)
            self.pubber3.publish(msg)
            time.sleep(0.1)

            if feedback_msg.remaining_dist < 0.2:
                break
        
        goal_handle.succeed()
        result = MyAction1.Result()
        result.pose_x = self.current_pose.x
        result.pose_y = self.current_pose.y
        result.pose_theta = self.current_pose.theta
        result.result_dist = self.total_dist

        self.total_dist = 0.0
        self.is_first_time = True
        
        return result
    
class TurtleSub_Act(TurtleSubber0_2):
    def __init__(self, act_server):
        super().__init__()
        self._act_server = act_server
    
    def sub_callback(self, msg): # Overriding
        #부모 sub_callback()의 latest_pose 갱신
        super().sub_callback(msg)
        #또는 그냥 self.latest_pose = msg 라고 직접 수정해도 되기는 함.
        self._act_server.current_pose = msg

def main(args=None):
    rclpy.init(args=args)

    executor = MultiThreadedExecutor()
    node_act = DistSrvr3()
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

if __name__ == '__main__':
    main()