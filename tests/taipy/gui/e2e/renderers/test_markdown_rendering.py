from importlib import util
import inspect
import logging

if util.find_spec("playwright"):
    from playwright._impl._page import Page

from taipy.gui import Gui


def test_markdown_render_with_style(page: "Page", gui: Gui, helpers):
    markdown_content = """
<|Hey|id=text1|>
<|There|id=text2|classname=custom-text|>
"""
    style = """
.taipy-text {
    color: green;
}
.custom-text {
    color: blue;
}
"""
    gui._set_frame(inspect.currentframe())
    gui.add_page("page1", markdown_content, style=style)
    helpers.run_e2e(gui)
    page.goto("/page1")
    page.expect_websocket()
    page.wait_for_selector("#text1")
    page.wait_for_selector("#Taipy_style", state="attached")
    html_style = page.query_selector("#Taipy_style")
    assert html_style.inner_text()
    function_evaluated = True
    try:
        page.wait_for_function('window.getComputedStyle(document.querySelector("#text1"), null).getPropertyValue("color") !== "rgb(255, 255, 255)"')
    except Exception as e:
        function_evaluated = False
        logging.getLogger().debug(f"Function evaluation timeout.\n{e}")
    if function_evaluated:
        assert (
            page.evaluate('window.getComputedStyle(document.querySelector("#text1"), null).getPropertyValue("color")')
            == "rgb(0, 128, 0)"
        )
        assert (
            page.evaluate('window.getComputedStyle(document.querySelector("#text2"), null).getPropertyValue("color")')
            == "rgb(0, 0, 255)"
        )
