import React, { Component } from 'react'
import { BrowserRouter as Router, Redirect, Route, Switch } from 'react-router-dom'
import { AppProvider } from './context/AppContext'

import 'bootstrap/dist/css/bootstrap.css'
import './assets/css/main.sass'

import Operator from './components/views/Operator'
import Viewer from './components/views/Viewer'

class App extends Component {
  render () {
    return (
      <AppProvider value={this.state}>
        <Router>
          <div className='App'>
            <Switch>
              <Route path='/' component={Operator} exact />
              <Route path='/viewer' component={Viewer} exact />
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
