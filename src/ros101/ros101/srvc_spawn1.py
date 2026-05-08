# 거북이 여러 개를 일정한 간격으로 원 위에 스폰시키기
import rclpy
from rclpy.node import Node
import time
import numpy as np

from turtlesim.srv import Spawn
from turtlesim.srv import TeleportAbsolute
from interface_pkg1.srv import MyService1

class MutiSpawnSrvc1(Node):
    def __init__(self):
        super().__init__("srvc_node2")

        #1. 서버 생성
        self.srvr1 = self.create_service(
            MyService1, 'srvc_req1', self.callback_srvc)
        #2. 클라 생성
        self.cli1_tele = self.create_client(
            TeleportAbsolute, '/turtle1/teleport_absolute')
        self.cli2_spawn = self.create_client(
            Spawn, '/spawn')
        #3. Request() 객체 생성
        self.req_tele = TeleportAbsolute.Request()
        self.req_spawn = Spawn.Request()
        #4. 기준 좌표
        self.center_x = 5.54
        self.center_y = 5.54
    
    #5. 좌표 계산 함수
    def calc_positions(self, n, r):
        theta_gap = 2*np.pi / n # n개 거북간 라디안 각도 간격: 2파이/n
        theta = [theta_gap*n for n in range(n)] #각 거북의 각도 배열
        x = [r*np.cos(th) for th in theta] #각 거북의 x좌표: 반지름*코사인(세타)
        y = [r*np.sin(th) for th in theta] #각 거북의 y좌표: 반지름*사인(세타)
        return x, y, theta
    
    #6. ROS 클라에게 좌표 배열 보내 스폰 요청 + 터미널 클라에게 response 
    def callback_srvc(self, request, response):
        
        x, y, theta = self.calc_positions(request.num, 3)

        # ROS 클라에게 보내줄 좌표 배열
        for n in range(len(theta)):
            self.req_spawn.x = x[n] + self.center_x
            self.req_spawn.y = y[n] + self.center_y
            self.req_spawn.theta = theta[n]
            self.cli2_spawn.call_async(self.req_spawn) #스폰 요청함
            time.sleep(0.1)

        # ROS 서버가 터미널 클라에게 보낼 response
        response.x = x
        response.y = y
        response.theta = theta

        return response

def main(args=None):
    rclpy.init(args=args)

    node1 = MutiSpawnSrvc1()
    rclpy.spin(node1)

    rclpy.shutdown()

if __name__=='__main__':
    main()