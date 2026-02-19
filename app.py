import tkinter as tk
from tkinter import messagebox


def on_test_button_click() -> None:
    messagebox.showinfo("테스트 메시지", "버튼이 정상적으로 동작합니다! ✅")


def main() -> None:
    root = tk.Tk()
    root.title("테스트 앱")
    root.geometry("320x180")
    root.resizable(False, False)

    title_label = tk.Label(
        root,
        text="오프라인 테스트 앱",
        font=("맑은 고딕", 14, "bold"),
        pady=20,
    )
    title_label.pack()

    test_button = tk.Button(
        root,
        text="테스트 버튼",
        font=("맑은 고딕", 11),
        width=18,
        height=2,
        command=on_test_button_click,
    )
    test_button.pack()

    helper_label = tk.Label(
        root,
        text="버튼을 누르면 메시지가 나타납니다.",
        font=("맑은 고딕", 9),
        pady=16,
    )
    helper_label.pack()

    root.mainloop()


if __name__ == "__main__":
    main()
