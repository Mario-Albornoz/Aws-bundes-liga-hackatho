const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// Required for Three.js asset loading (obj, mtl, etc.)
config.resolver.assetExts.push('obj', 'mtl', 'dae', 'glb', 'gltf');

module.exports = config;