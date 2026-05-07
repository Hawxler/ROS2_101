# 거북이를 1.0, 1.0 위치로 순간이동 + 임의값 출력
import rclpy
from rclpy.node import Node

from turtlesim.srv import TeleportAbsolute
from interface_pkg1.srv import MyService1

class TeleportSrvc1(Node):
    def __init__(self):
        super().__init__("srvc_node0")

        #1. 서버 생성
        # 터미널 클라에서 -> srvc_req0 요청 -> ROS srvr1: ros2 service call /srvc_req0 interface_pkg1/srv/MyService1 "{num: 1}" 하면 콜백 실행
        self.srvr1 = self.create_service(
            MyService1, 
            'srvc_req0',
            self.srvc_callback
        )

        #2. 순간 이동 클라 생성
        # ROS srvr1 callback -> ROS cli_tele1 -> Request().x, Request().y -> 터틀심 서버
        self.cli_tele1 = self.create_client(
            TeleportAbsolute, 
            '/turtle1/teleport_absolute'
        )

        #3. 터틀심에게 보낼 Request 객체 생성: Request().x, Request().y
        self.req_teleport = TeleportAbsolute.Request()

    # 외부에서 /srvc_topic0 요청(request.num 1)이 들어모면 서버 콜백 실행
    # response는 결과를 담아서 돌려줄 빈 응답 객체
    def srvc_callback(self, request, response):
        self.req_teleport.x = 1.0
        self.req_teleport.y = 1.0
        future = self.cli_tele1.call_async(self.req_teleport)
        if future.result is not None: # 터틀심이 값 없는 객체만 보내옴
            print("Request recieved by Turtlesim.")
        response.x = [100.0] # 터미널 클라에게 보낼 임의의 값 대입함.
        response.y = [100.0]
        response.theta = [1.57]
        return response # 터미널 클라에게 리턴해줌.
    
def main(args=None):
    rclpy.init(args=args)

    node1 = TeleportSrvc1()
    rclpy.spin(node1)

    rclpy.shutdown()

if __name__ == '__main__':
    main()