import React, { Component } from 'react'
import { BrowserRouter as Router, Redirect, Route, Switch } from 'react-router-dom'
import { AppProvider } from './context/AppContext'

import 'bootstrap/dist/css/bootstrap.css'
import './assets/css/main.sass'

import Operate from './components/views/Operate'

class App extends Component {
  render () {
    // TODO move to template
    const meta = document.createElement('meta')
    meta.name = 'google'
    meta.content = 'notranslate'
    document.getElementsByTagName('head')[0].appendChild(meta)
    return (
      <AppProvider value={this.state}>
        <Router>
          <div className='App'>
            <Switch>
              <Route path='/' component={Operate} exact />
              <Route>
                <Redirect to='/' />
              </Route>
            </Switch>
          </div>
        </Router>
      </AppProvider>
    )
  }
}

export default App
