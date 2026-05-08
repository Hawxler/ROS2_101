# 1번 파일에 Feedback 추가
import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node
import time

from interface_pkg1.action import MyAction1

class DistSrvr2(Node):
    def __init__(self):
        super().__init__("act_srvr_node2")
        self.srvr_act2 = ActionServer(
            self,
            MyAction1,
            'dist_action2',
            self.execute_callback
        )

    def execute_callback(self, goal_handle):
        feedback_msg = MyAction1.Feedback()
        for n in range(10, 0, -1):
            feedback_msg.remaining_dist = float(n)
            goal_handle.publish_feedback(feedback_msg)
            time.sleep(0.5)

        goal_handle.succeed()
        result = MyAction1.Result()
        return result

def main(args=None):
    rclpy.init(args=args)

    node1 = DistSrvr2()
    rclpy.spin(node1)

    rclpy.shutdown()

if __name__=='__main__':
    main()