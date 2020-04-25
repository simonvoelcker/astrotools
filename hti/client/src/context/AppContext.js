import React, { Component } from 'react'
import $backend from '../backend'

export const AppContext = React.createContext()

export class AppProvider extends Component {
  constructor (props) {
    super(props)
    this.state = {
    }

    this.mutations = {
      getAxisSpeed: (axis) => {
        $backend.getAxisSpeed(axis)
          .then(response => {
            console.log('Success, ' + response)
          }).catch(error => {
            console.log('Error, ' + error)
          })
      }
    }
  }

  componentDidMount () {
    // something
  }

  render () {
    return (
      <AppContext.Provider value={{ store: this.state, mutations: this.mutations }}>
        {this.props.children}
      </AppContext.Provider>
    )
  }
}

export const AppConsumer = AppContext.Consumer
