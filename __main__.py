from src.app import App


def main():
    root = App()
    root.navbar.display_home_frame()
    root.window.mainloop()


if __name__ == "__main__":
    main()
