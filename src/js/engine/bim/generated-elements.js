
function bimGelKey(gen, path) {
  if (typeof gen !== 'string' || gen === '' || gen.includes('|') || gen.includes('/') || gen.includes(':')) {
    return { error: 'bad generator id' }
  }
  if (!Array.isArray(path) || path.length === 0) {
    return { error: 'empty path' }
  }
  var parts = []
  for (var i = 0; i < path.length; i++) {
    var entry = path[i]
    if (!Array.isArray(entry) || entry.length !== 2) {
      return { error: 'bad rule name at ' + i }
    }
    var rule = entry[0]
    var index = entry[1]
    if (typeof rule !== 'string' || rule === '' || rule.includes('|') || rule.includes('/') || rule.includes(':')) {
      return { error: 'bad rule name at ' + i }
    }
    if (typeof index === 'number') {
      if (!Number.isInteger(index) || index < 0) {
        return { error: 'bad index at ' + i }
      }
    } else if (typeof index === 'string') {
      if (index === '' || index.includes('|') || index.includes('/') || index.includes(':')) {
        return { error: 'bad index at ' + i }
      }
    } else {
      return { error: 'bad index at ' + i }
    }
    parts.push(rule + ':' + index)
  }
  return { key: gen + '|' + parts.join('/') }
}

function bimGelShape(key) {
  if (typeof key !== 'string') {
    return key
  }
  var idx = key.indexOf('|')
  if (idx === -1) {
    return key
  }
  var prefix = key.substring(0, idx + 1)
  var rest = key.substring(idx + 1)
  var parts = rest.split('/')
  var result = []
  for (var i = 0; i < parts.length; i++) {
    var part = parts[i]
    var colonIdx = part.lastIndexOf(':')
    if (colonIdx === -1) {
      result.push(part)
    } else {
      var prop = part.substring(0, colonIdx)
      var idxPart = part.substring(colonIdx + 1)
      if (/^\d+$/.test(idxPart)) {
        result.push(prop + ':*')
      } else {
        result.push(prop + ':' + idxPart)
      }
    }
  }
  return prefix + result.join('/')
}

function bimGelReconcile(existing, derived) {
  var keyCount = {}
  for (var i = 0; i < derived.length; i++) {
    var item = derived[i]
    var k = item.key
    if (keyCount[k] !== undefined) {
      return { error: 'duplicate key ' + k }
    }
    keyCount[k] = true
  }

  var existingMap = {}
  for (var i = 0; i < existing.length; i++) {
    var elem = existing[i]
    if (!(elem.key in existingMap)) {
      existingMap[elem.key] = elem
    }
  }

  var update = []
  var create = []
  var removeIds = []
  var matched = new Set()

  for (var i = 0; i < derived.length; i++) {
    var derivedItem = derived[i]
    var key = derivedItem.key
    if (key in existingMap) {
      var existingElem = existingMap[key]
      update.push({ id: existingElem.id, item: derivedItem })
      matched.add(existingElem.id)
    } else {
      create.push(derivedItem)
    }
  }

  for (var i = 0; i < existing.length; i++) {
    var elem = existing[i]
    if (!matched.has(elem.id)) {
      removeIds.push(elem.id)
    }
  }

  return { update: update, create: create, remove: removeIds }
}

function bimGelOverrides(overrides, keys) {
  var apply = []
  var dormant = []
  var listed = []
  for (var i = 0; i < overrides.length; i++) {
    var override = overrides[i]
    var key = override.key
    if (keys.indexOf(key) >= 0) {
      apply.push(override)
    } else {
      var overrideShape = bimGelShape(key)
      var hasMatchingKey = false
      for (var j = 0; j < keys.length; j++) {
        if (bimGelShape(keys[j]) === overrideShape) {
          hasMatchingKey = true
          break
        }
      }
      if (hasMatchingKey) {
        dormant.push(override)
      } else {
        listed.push(override)
      }
    }
  }
  return { apply: apply, dormant: dormant, listed: listed }
}

function bimGelApply(item, overrides) {
  var newProps
  if (item.props) {
    newProps = {}
    for (var prop in item.props) {
      newProps[prop] = item.props[prop]
    }
  } else {
    newProps = {}
  }
  var ov = []
  for (var j = 0; j < overrides.length; j++) {
    var override = overrides[j]
    if (override.key === item.key) {
      var prop = override.prop
      var value = override.value
      newProps[prop] = value
      var ovHas = false
      for (var k = 0; k < ov.length; k++) {
        if (ov[k] === prop) {
          ovHas = true
          break
        }
      }
      if (!ovHas) {
        ov.push(prop)
      }
    }
  }
  var result = {
    key: item.key,
    props: newProps,
    ov: ov
  }
  if (item.kind !== undefined) {
    result.kind = item.kind
  }
  return result
}
