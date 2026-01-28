/**
 * 初始化加载效果的svg格式logo
 * @param {string} id - 元素id
 */
 function initSvgLogo(id) {
  // const svgStr = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500"><g id="freepik--Chicken--inject-358"><g><g><path d=""></path></g></g></g></svg>`
  const appEl = document.querySelector(id)
  const div = document.createElement('div')
  // div.innerHTML = svgStr
  if (appEl) {
    appEl.appendChild(div)
  }
}

function addThemeColorCssVars() {
  const key = '__THEME_COLOR__'
  const defaultColor = '#F4511E'
  const themeColor = window.localStorage.getItem(key) || defaultColor
  const cssVars = `--primary-color: ${themeColor}`
  document.documentElement.style.cssText = cssVars
}

addThemeColorCssVars()

initSvgLogo('#loadingLogo')
