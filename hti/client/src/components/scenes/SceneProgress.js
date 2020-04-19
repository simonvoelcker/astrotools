import React, { Component } from 'react'
import ModelProgress from '../panels/ModelProgress'
import CircularProgressIndicator from '../panels/CircularProgressIndicator'
import { AppConsumer } from '../../context/AppContext'

export default class SceneProgress extends Component {
  constructor (props) {
    super(props)
    this.state = {
      height: 768
    }
  }
  componentDidMount () {
    this.resize()
    window.addEventListener('resize', this.resize)
  }

  resize = () => {
    // first, check if element is currently available...
    if (!this.centeredElement) { return }
    // ... then resize
    const height = this.centeredElement.clientHeight
    if (height !== this.state.height) {
      this.setState({ height })
    }
  }

  render () {
    const { height } = this.state
    return (
      <AppConsumer>

        {({ store }) => (
          <div className='scene scene-progress' style={store.selectedScene === 'SceneProgress' ? { opacity: 1, zIndex: 1 } : { opacity: 0, zIndex: -1 }}>
            <div ref={centeredElement => { this.centeredElement = centeredElement }} className='centered' style={{ width: height }}>
              <CircularProgressIndicator />
              <ModelProgress stlFileName={store.stlFileName} key={store.stlFileName} />
            </div>
          </div>
        )}

      </AppConsumer>
    )
  }
}
