import React, { Component } from 'react'
import { BrowserRouter as Router, Redirect, Route, Switch } from 'react-router-dom'
import { AppProvider } from './context/AppContext'

import 'bootstrap/dist/css/bootstrap.css'
import './assets/css/main.sass'

import Manage from './components/views/Manage'
import Operate from './components/views/Operate'
import Report from './components/views/Report'
import MachineInfo from './components/views/MachineInfo'

class App extends Component {
  render () {
    // When the HMI starts, a Dialog pops up that suggests to translate the page.
    // This should not be.
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

              <Route path='/manage' component={Manage} />

              <Route path='/report' component={Report} />

              <Route path='/machine-info' component={MachineInfo} />

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
