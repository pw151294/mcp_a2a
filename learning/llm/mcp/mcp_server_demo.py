import json
import logging
import os.path
import subprocess
import uuid

from mcp.server.fastmcp import FastMCP

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("mcp.log"),
    ]
)
logger = logging.getLogger(__name__)

mcp = FastMCP()
mcp.settings.host = "localhost"
mcp.settings.port = 9888
mcp.settings.streamable_http_path = "/calculator/mcp"

BASE_DIR = '/Users/panwei/Downloads/python/mcp+A2A/mcp_a2a/learning/llm/mcp'
UV_CMD = "uv"


@mcp.tool()
async def calculator(expression: str) -> str:
    """一个数学计算器 用来计算传递的Python数学表达式
    Args:
        expression: 符合Python eval()函数调用的数学表达式
    Returns
        表达式的计算结果
    """
    try:
        result = eval(expression)
        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"result": f"数学表达式计算出错：{str(e)}"})


@mcp.tool()
async def bash(command: str) -> dict:
    """传递command指令 在macos下执行cmd指令

    Args:
        command: 需要执行的cmd指令

    Returns:
        指令执行结果的字典
    """
    result = subprocess.run(
        command,
        shell=True,  # 让命令行通过cmd执行
        capture_output=True,  # 捕获输出结果
        text=True,  # 输出解码为字符串
    )

    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


@mcp.tool()
async def run_code(language: str, code: str, timeout: int = 30) -> str | None:
    """根据语言执行代码并返回运行结果 Python代码会使用uv创建的Python3.11版本

    Args:
        language: 代码语言 支持 python/nodejs
        code: 需要执行的代码
        timeout: 代码执行超时时间 默认30秒

    Returns:
        执行输出(stdout)或者是错误信息(stderr)
    """
    # 检查传递的编程语言是否是Python/nodejs
    language = (language or "").strip().lower()
    if language not in ("python", "nodejs"):
        return f"不支持的编程语言：{language}，目前仅支持 python/nodejs"

    # 计算获取临时代码的文件名称
    suffix = ".py" if language == "python" else ".js"
    name = f"temp_{uuid.uuid4().hex}{suffix}"
    tmp_path = os.path.join(BASE_DIR, name)

    # 确保目录存在
    os.makedirs(BASE_DIR, exist_ok=True)

    try:
        # 将代码写入到临时文件中
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(code)

        cwd = BASE_DIR
        # 根据语言选择执行命令
        if language == "python":
            cmd = [UV_CMD, "--directory", BASE_DIR, "run", name]
        else:  # nodejs
            cmd = ["node", tmp_path]

        # 调用子线程运行对应命令
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd
        )

        # 获取输出和错误结果
        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()

        # 判断状态码
        if proc.returncode == 0:
            return stdout
        else:
            return f"代码执行出错，错误信息：{stderr}"
    except subprocess.TimeoutExpired:
        return f"代码执行超时，超过 {timeout} 秒未完成"
    except FileNotFoundError as e:
        return f"执行命令未找到：{str(e)}"
    except Exception as e:
        return f"代码执行出错：{str(e)}"
    finally:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception as e:
            logger.error(f"删除临时代码文件失败：{str(e)}")


if __name__ == '__main__':
    mcp.run(transport="streamable-http")
