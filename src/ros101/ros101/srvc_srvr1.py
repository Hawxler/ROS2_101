#기초 연습: request.num을 받으면 x, y, theta 배열을 response로 돌려주는 서버
import rclpy
from rclpy.node import Node

from interface_pkg1.srv import MyService1

class MultiSpawnSrvc1(Node):
    def __init__(self):
        super().__init__('srv_node1')
        self.srvr1 = self.create_service(
            MyService1, 
            'srvc_topic1',
            self.srvc_callback
        )
    ################################
    # int64 num
    # ---
    # float64[] x
    # float64[] y
    # float64[] theta
    #################################
    
    # 누군가 request를 날리면 아래 콜백 실행
    def srvc_callback(self, request, response):
        print("Request:", request)

        response.x = [1., 2., 3.]
        response.y = [10., 20.]
        response.theta = [100., 200., 300.]

        return response
    
def main(args=None):
    rclpy.init(args=args)

    node1 = MultiSpawnSrvc1()
    rclpy.spin(node1)

    rclpy.shutdown()

if __name__=='__main__':
    main()