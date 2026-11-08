
import config
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from supervisor import build_supervisor
from tracing import DEFAULT_USER_ID, make_run_config


def message_text(message):
    """Mengambil teks dari sebuah pesan (isinya bisa berupa teks biasa atau daftar potongan)."""
    content = message.content
    if isinstance(content, str):
        return content
    text = ""
    for part in content:
        if isinstance(part, str):
            text = text + part
        elif isinstance(part, dict) and part.get("type") == "text":
            text = text + part.get("text", "")
    return text


def build_input_messages(history, question):
    """Mengubah riwayat chat + pertanyaan baru menjadi daftar pesan untuk supervisor.
    Hanya CHAT_HISTORY_TURNS giliran terakhir yang dikirim (1 giliran = 1 pertanyaan + 1 jawaban),
    supaya biaya token tidak membengkak."""
    max_messages = config.CHAT_HISTORY_TURNS * 2
    recent_history = history[-max_messages:] if history else []

    messages = []
    for item in recent_history:
        if item["role"] == "user":
            messages.append(HumanMessage(content=item["content"]))
        else:
            messages.append(AIMessage(content=item["content"]))
    messages.append(HumanMessage(content=question))
    return messages


def extract_tool_calls(new_messages):
    """Mengumpulkan semua pemanggilan tool dari pesan-pesan baru, lengkap dengan hasilnya.
    Pemanggilan 'transfer_to_...' adalah serah-terima antar agent (handoff), bukan tool data."""
    calls = []
    calls_by_id = {}

    for message in new_messages:
        if isinstance(message, AIMessage):
            for tool_call in message.tool_calls:
                tool_name = tool_call["name"]
                is_handoff = tool_name.startswith("transfer_to_") or tool_name.startswith("transfer_back_to")
                call = {
                    "agent": message.name,          
                    "tool": tool_name,
                    "arguments": tool_call["args"],
                    "output": "",
                    "is_handoff": is_handoff,
                }
                calls.append(call)
                calls_by_id[tool_call["id"]] = call
        elif isinstance(message, ToolMessage):
            call = calls_by_id.get(message.tool_call_id)
            if call is not None:
                call["output"] = message_text(message)

    return calls


def sum_usage(new_messages):
    """Menjumlahkan token dari SEMUA panggilan LLM (supervisor + agent anak buah) di satu pertanyaan."""
    input_tokens = 0
    output_tokens = 0
    llm_calls = 0
    for message in new_messages:
        if isinstance(message, AIMessage) and message.usage_metadata:
            input_tokens = input_tokens + message.usage_metadata.get("input_tokens", 0)
            output_tokens = output_tokens + message.usage_metadata.get("output_tokens", 0)
            llm_calls = llm_calls + 1
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "llm_calls": llm_calls,
    }


def find_final_answer(new_messages):
    """Jawaban akhir = pesan AI terakhir yang berisi teks dan BUKAN pesan 'Transferring back...'."""
    for message in reversed(new_messages):
        if not isinstance(message, AIMessage):
            continue
        if message.response_metadata.get("__is_handoff_back"):
            continue
        text = message_text(message).strip()
        if text != "":
            return text
    return ""


def analyze_messages(new_messages):
    """Mengubah daftar pesan baru menjadi hasil rapi: jawaban, tool calls, usage."""
    return {
        "answer": find_final_answer(new_messages),
        "tool_calls": extract_tool_calls(new_messages),
        "usage": sum_usage(new_messages),
        "messages": new_messages,
    }


def ask(question, history, session_id, supervisor=None, user_id=None, tags=None):
    """Bertanya ke chatbot (supervisor) dan mengembalikan hasil yang sudah dirapikan.

    supervisor: kalau tidak diisi, supervisor dibuat baru setiap pertanyaan. Ini murah, dan membuat
    perubahan prompt di Langfuse langsung terpakai (tanpa restart aplikasi).
    """
    if supervisor is None:
        supervisor = build_supervisor()

    input_messages = build_input_messages(history, question)

    if user_id is None:
        user_id = DEFAULT_USER_ID
    if tags is None:
        tags = ["capstone", "supervisor"]

    run_config = make_run_config(session_id=session_id, user_id=user_id, tags=tags)

    result = supervisor.invoke({"messages": input_messages}, config=run_config)

    new_messages = result["messages"][len(input_messages):]
    return analyze_messages(new_messages)


def print_report(result):
    """Mencetak hasil satu pertanyaan ke terminal (untuk skrip tes)."""
    print("--- Tool calls ---")
    shown = 0
    for call in result["tool_calls"]:
        if call["is_handoff"]:
            print("  [serah-terima]", call["agent"], "->", call["tool"])
        else:
            shown = shown + 1
            print("  [tool]", call["agent"], "memanggil", call["tool"], call["arguments"])
            output_preview = call["output"].replace("\n", " ")[:300]
            print("         hasil:", output_preview)
    if shown == 0:
        print("  (tidak ada tool data yang dipanggil)")

    usage = result["usage"]
    print("--- Usage ---")
    print("  input:", usage["input_tokens"], "| output:", usage["output_tokens"],
          "| total:", usage["total_tokens"], "| panggilan LLM:", usage["llm_calls"])
    print("--- Jawaban ---")
    print(result["answer"])
