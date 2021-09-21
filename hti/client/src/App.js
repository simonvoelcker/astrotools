import React, { Component } from 'react'
import { AppProvider } from './context/AppContext'

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

export default App
