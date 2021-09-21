import React, { Component } from 'react'
import ReactDOM from 'react-dom'
import { AppProvider } from './appstate'

import 'bootstrap/dist/css/bootstrap.css'
import './assets/css/main.sass'

import Operator from './components/views/Operator'

class App extends Component {
  render () {
    return (
      <AppProvider value={this.state}>
        <Operator />
      </AppProvider>
    )
  }
}

ReactDOM.render(<App />, document.getElementById('root'))
