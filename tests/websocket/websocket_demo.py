def main(request_data: str) -> dict:
    import json
    import threading
    import time
    import os
    import websocket

    class WebSocketClient:

        def __init__(self, url, request_data):
            self.url = url
            self.request_data = request_data
            self.content_parts = []
            self.is_finished = False
            self.error_message = None

        def on_message(self, ws, message):
            try:
                data = json.loads(message)
                print(f"收到消息: {json.dumps(data, ensure_ascii=False, indent=2)}")
                header_status = data.get("header", {}).get("status")
                payload_status = data.get("payload", {}).get("choices", {}).get("status")
                text_list = data.get("payload", {}).get("choices", {}).get("text", [])
                for text_item in text_list:
                    content = text_item.get("content", "")
                    if content:
                        self.content_parts.append(content)
                if header_status == 2 or payload_status == 2:
                    self.is_finished = True
                    print("收到结束信号 (status=2)")
            except json.JSONDecodeError as e:
                self.error_message = f"JSON解析错误: {str(e)}"
                print(f"错误: {self.error_message}")
            except Exception as e:
                self.error_message = f"处理消息时出错: {str(e)}"
                print(f"错误: {self.error_message}")

        def on_error(self, ws, error):
            self.error_message = f"WebSocket错误: {str(error)}"
            print(f"错误: {self.error_message}")

        def on_close(self, ws, close_status_code, close_msg):
            print("WebSocket连接已关闭")

        def on_open(self, ws):
            print("WebSocket连接已建立")
            request_json = json.dumps(self.request_data, ensure_ascii=False)
            print(f"发送请求: {request_json}")
            ws.send(request_json)

        def run(self):
            ws = websocket.WebSocketApp(
                self.url,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
                on_open=self.on_open
            )

            # 禁用代理，直接连接 - 临时清除代理环境变量
            old_proxy = os.environ.get('http_proxy')
            old_https_proxy = os.environ.get('https_proxy')
            old_ws_proxy = os.environ.get('ws_proxy')
            old_wss_proxy = os.environ.get('wss_proxy')
            old_HTTP_PROXY = os.environ.get('HTTP_PROXY')
            old_HTTPS_PROXY = os.environ.get('HTTPS_PROXY')
            old_WS_PROXY = os.environ.get('WS_PROXY')
            old_WSS_PROXY = os.environ.get('WSS_PROXY')

            try:
                # 清除所有代理环境变量
                for key in ['http_proxy', 'https_proxy', 'ws_proxy', 'wss_proxy',
                            'HTTP_PROXY', 'HTTPS_PROXY', 'WS_PROXY', 'WSS_PROXY']:
                    os.environ.pop(key, None)

                wst = threading.Thread(target=ws.run_forever)
                wst.daemon = True
                wst.start()

                time.sleep(1)

                timeout = 60
                start_time = time.time()

                while not self.is_finished and not self.error_message:
                    if time.time() - start_time > timeout:
                        self.error_message = "请求超时"
                        break
                    time.sleep(0.1)

                ws.close()
                wst.join(timeout=2)
            finally:
                # 恢复代理环境变量
                if old_proxy:
                    os.environ['http_proxy'] = old_proxy
                if old_https_proxy:
                    os.environ['https_proxy'] = old_https_proxy
                if old_ws_proxy:
                    os.environ['ws_proxy'] = old_ws_proxy
                if old_wss_proxy:
                    os.environ['wss_proxy'] = old_wss_proxy
                if old_HTTP_PROXY:
                    os.environ['HTTP_PROXY'] = old_HTTP_PROXY
                if old_HTTPS_PROXY:
                    os.environ['HTTPS_PROXY'] = old_HTTPS_PROXY
                if old_WS_PROXY:
                    os.environ['WS_PROXY'] = old_WS_PROXY
                if old_WSS_PROXY:
                    os.environ['WSS_PROXY'] = old_WSS_PROXY

            if self.error_message:
                raise Exception(self.error_message)

            result = "".join(self.content_parts)
            return result

    def websocket_request(url, request_data):
        client = WebSocketClient(url, request_data)
        return client.run()

    url = "ws://172.31.186.98:8905/agent/proxyApi/flames-docqa/doc/v1/chat"
    # 如果request_data是字符串，则解析为字典
    if isinstance(request_data, str):
        try:
            request_data = json.loads(request_data)
        except json.JSONDecodeError:
            raise ValueError("request_data必须是有效的JSON字符串或字典")
    return {
        "result": websocket_request(url, request_data)
    }


if __name__ == '__main__':
    print(main('1234'))
