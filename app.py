from ui.WebUI import WebUI
app = WebUI.init()


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)