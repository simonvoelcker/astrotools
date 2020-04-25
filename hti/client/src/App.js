import React, { Component } from 'react'
import { BrowserRouter as Router, Redirect, Route, Switch } from 'react-router-dom'
import { AppProvider } from './context/AppContext'

import 'bootstrap/dist/css/bootstrap.css'
import './assets/css/main.sass'

import Operate from './components/views/Operate'

class App extends Component {
  render () {
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
