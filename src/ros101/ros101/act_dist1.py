# Action의 기본 구조만 보여주는 연습용 코드
import rclpy
from rclpy.node import Node

from rclpy.action import ActionServer
from interface_pkg1.action import MyAction1

class DistSrvr1(Node):
    def __init__(self):
        super().__init__('act_srvr_node1')

        self.srvr_act1 = ActionServer(
            self,
            MyAction1,
            'dist_action1',
            self.callback_exe
        )

    #2. Goal 수신 시 실행됨.
    ####Goal 관리하는 goal_handle 개체####
    # goal_handle.request
    # goal_handle.succeed()
    # goal_handle.abort()
    # goal_handle.canceled()
    # goal_handle.publish_feedback()
    ###################################
    def callback_exe(self, goal_handle):
        # 성공 상태로 만듦.
        goal_handle.succeed() 
        
        # 클라에게 반환할 메시지 객체 생성
        result = MyAction1.Result()
        #예: result.result_dist = 3.0

        return result # 클라에게 리턴 필수. 그래야 모든 사항이 처리됨.
    
def main(args=None):
    rclpy.init(args=args)

    node1 = DistSrvr1()
    rclpy.spin(node1)

    rclpy.shutdown()

if __name__=='__main__':
    main()