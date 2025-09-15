// Test script for truncateText function
function truncateText(text, maxLength) {
  // Handle all edge cases explicitly
  if (text === null || text === undefined || typeof text !== 'string') {
    return ''
  }
  
  // Ensure text is definitely a string and has length property
  const safeText = String(text)
  if (safeText.length <= maxLength) return safeText
  return safeText.slice(0, maxLength) + '...'
}

// Test cases
console.log('Testing truncateText function:')
console.log('undefined:', truncateText(undefined, 10))
console.log('null:', truncateText(null, 10))
console.log('empty string:', truncateText('', 10))
console.log('short text:', truncateText('hello', 10))
console.log('long text:', truncateText('this is a very long text that should be truncated', 10))
console.log('number:', truncateText(123, 10))
console.log('object:', truncateText({}, 10))